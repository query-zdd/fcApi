# -*- coding:UTF-8 -*-
import logging
import types

import django
from django.db import models
from decimal import *

from django.db.models import Q
from django.db.models.base import ModelState
from datetime import datetime, date

from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import  render
from django.conf import settings
import urllib
import os
import json
# from PIL import Image,ImageDraw,ImageFont
import random
import functools
from lin.models import *
# 获取注意事项数据以及确认数据
def getNotesNum(plan_id=None,order_id=None):
    if not plan_id:
        orderObj = PlanOrder.objects.get(id=order_id,delete_time=None)
        plan_id = orderObj.plan_id
    notes_sure_num = 0
    notes_all_num = 0
    orderNotes = OrderNotes.objects.filter(plan_id=plan_id,delete_time=None)
    orderOtherNotes = OrderNotesOther.objects.filter(plan_id=plan_id,delete_time=None)
    notes_all_num = orderOtherNotes.count() + orderNotes.count()
    for one in orderOtherNotes:
        if one.is_sure ==1:
            notes_sure_num = notes_sure_num + 1
    for one1 in orderNotes:
        if one1.is_sure == 1:
            notes_sure_num = notes_sure_num + 1
    return notes_all_num, notes_sure_num
#获取计划上手时间
def getPlanStartdate(order_id):
    fmObj = FactoryMake.objects.filter(order_id=order_id,delete_time=None)
    str_time = datetime.now()
    plan_start_date_list= []
    for o1 in fmObj:
        if o1.plan_start_date:
            plan_start_date_list.append(o1.plan_start_date)
    if plan_start_date_list:
        plan_start_date = min(plan_start_date_list)
        down_day = downDay(str_time,plan_start_date)
    else:
        plan_start_date = None
        down_day = None
    return plan_start_date, down_day

#获取实际计划上手时间
def getRealStartdate(order_id):
    fmObj = FactoryMake.objects.filter(order_id=order_id,delete_time=None)
    str_time = datetime.now()
    plan_real_date_list= []
    for o1 in fmObj:
        if o1.real_start_date:
            plan_real_date_list.append(o1.real_start_date)
    if plan_real_date_list:
        real_start_date = min(plan_real_date_list)
        down_day = downDay(str_time,real_start_date)
    else:
        real_start_date = None
        down_day = None
    return real_start_date, down_day

# 获取短溢装和短溢装数量
def getOverflow(order_id):
    orderLine = PlanOrderLine.objects.filter(order_id=order_id,delete_time=None)
    short_overflow_num = 0
    contract_num = 0
    for one in orderLine:
        short_overflow_num +=(one.order_num  - one.contract_num)
        contract_num += one.contract_num
    short_overflow =round(short_overflow_num/contract_num,2)
    return short_overflow_num,short_overflow

# 录入装箱要求数量以及完成数量
def getpackNum(order_id):
    orderLine = PlanOrderLine.objects.filter(order_id = order_id,delete_time=None)
    pack_num = orderLine.count()
    pack_sure_num = 0
    packObj = OrderLinePacking.objects.filter(order_id = order_id,delete_time=None)
    for one in packObj:
        # 状态，0：无装箱指示，1：有装箱指示（分订单项指示）；2：统一指示
        if one.status !=0:
            pack_sure_num = pack_sure_num+1
    return pack_num,pack_sure_num

# 面辅料确认数目
def getClothSureNum(order_id):
    orderCloth = OrderCloth.objects.filter(order_id=order_id,delete_time=None)
    order_cloth_num = orderCloth.count()
    order_cloth_sure_num = 0
    for one in orderCloth:
        if one.is_sure == 1:
            order_cloth_sure_num += 1
    return order_cloth_num, order_cloth_sure_num

# 面辅料入库数量
def getClothInStore(order_id):
    orderCloth = OrderCloth.objects.filter(order_id=order_id,delete_time=None)
    order_cloth_store_num = orderCloth.count()
    order_cloth_store_sure_num = 0
    for one in orderCloth:
        if one.is_sure_in_store == 1:
            order_cloth_store_sure_num += 1
    return order_cloth_store_num, order_cloth_store_sure_num

# 成衣样品数量与确认
def getPlanSampleNum(order_id):
    orderObj = PlanOrder.objects.get(id=order_id,delete_time=None)
    pclsObj = PlanClothSampleLine.objects.filter(plan_id=orderObj.plan_id,delete_time=None)
    sample_num = pclsObj.count()
    sample_sure_num = 0
    for one in pclsObj:
        if one.is_sure ==1:
            sample_sure_num +=1
    return sample_num, sample_sure_num

# 洗标吊牌数据
def getDropLableNum(order_id):
    orderLineObj = PlanOrderLine.objects.filter(order_id=order_id,delete_time=None)
    drop_lable_num = orderLineObj.count()
    drop_lable_sure_num = 0
    for one in orderLineObj:
        if one.lable_url and one.drop_url:
            drop_lable_sure_num += 1

    return  drop_lable_num,drop_lable_sure_num

# 面辅料确认接口
def clothSure(order_id):
    try:
        flag10 = 1
        flag11 = 1
        flag20 = 1
        flag21 = 1
        orderCloth = OrderCloth.objects.filter(order_id=order_id,delete_time=None)
        for one in orderCloth:
            orderClothShip = OrderClothShip.objects.filter(order_cloth_id=one.id,delete_time=None)
            for one1 in orderClothShip:
                # 子类类别处理
                orderClothShipLine = OrderClothLineShip.objects.filter(order_cloth_ship_id=one1.id,delete_time=None)
                for one2 in orderClothShipLine:
                    if one2.is_sure !=1:
                        flag10 = 0
                    if one2.is_sure_in_store !=1:
                        flag20 = 0
                if flag10 == 1:
                    one1.is_sure = 1
                if flag20 == 1:
                    one1.is_sure_in_store = 1
                one1.save()
                #父类列别处理
                if one1.is_sure != 1:
                    flag11 = 0
                if one1.is_sure_in_store != 1:
                    flag21 = 0
            if flag11 == 1:
                one.is_sure = 1
            if flag21 == 1:
                one.is_sure_in_store = 1
        return 1
    except:
        return 0

# 获取面辅料分类列表
def getClothCat(order_id):
    orderCloth = OrderCloth.objects.filter(order_id = order_id,delete_time=None)
    cloth_cat_list = []
    supplier_list = []
    delivery_name_list = []
    for one in orderCloth:
        # 分类
        cloth_cat = one.cloth_cat
        cloth_name = one.cloth_name
        clothClass = ClothClass.objects.filter(cloth_class_name=cloth_cat,delete_time=None)
        if clothClass.count()>0:
            flag = 0
            for one1 in cloth_cat_list:
                if one1['cloth_cat'] == cloth_cat:
                    one1['cloth_name_list'].append(cloth_name)
                    flag = 1
            if flag == 0:
                samp = {}
                rilt = []
                rilt.append(cloth_name)
                samp['cloth_cat'] = clothClass[0].cloth_class_name
                samp['cloth_cat_id'] = clothClass[0].id
                samp['cloth_name_list'] = rilt
                cloth_cat_list.append(samp)
    #供应商
    orderClothship = OrderClothShip.objects.filter(order_id = order_id,delete_time=None)
    for one2 in orderClothship:
        if one2.supplier not in supplier_list:
            supplier_list.append(one2.supplier)
    # 收货方
    orderClothshipLine = OrderClothLineShip.objects.filter(order_id=order_id,delete_time=None)
    for one3 in orderClothshipLine:
        if one3.delivery_name not in delivery_name_list:
            delivery_name_list.append(one3.delivery_name)

    return cloth_cat_list,supplier_list,delivery_name_list



# 日期之差
def downDay(d1,d2):
    if d1 and d2:
        dayNum = (d2.date()-d1.date()).days
    else:
        dayNum = None
    return dayNum
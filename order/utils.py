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
        orderObj = PlanOrder.objects.get(id=order_id)
        plan_id = orderObj.plan_id
    notes_sure_num = 0
    notes_all_num = 0
    orderNotes = OrderNotes.objects.filter(plan_id=plan_id)
    orderOtherNotes = OrderNotesOther.objects.filter(plan_id=plan_id)
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
    fmObj = FactoryMake.objects.filter(order_id=order_id)
    str_time = datetime.now()
    plan_start_date_list= []
    for o1 in fmObj:
        if o1.plan_start_date:
            plan_start_date_list.append(o1.plan_start_date)
    if plan_start_date_list:
        plan_start_date = min(plan_start_date_list)
        down_day = downDay(plan_start_date ,str_time)
    else:
        plan_start_date = None
        down_day = None
    return plan_start_date, down_day

# 获取短溢装和短溢装数量
def getOverflow(order_id):
    orderLine = PlanOrderLine.objects.filter(order_id=order_id)
    short_overflow_num = 0
    contract_num = 0
    for one in orderLine:
        short_overflow_num +=(one.order_num  - one.contract_num)
        contract_num += one.contract_num
    short_overflow =round(short_overflow_num/contract_num,2)
    return short_overflow_num,short_overflow

# 录入装箱要求数量以及完成数量
def getpackNum(order_id):
    orderLine = PlanOrderLine.objects.filter(order_id = order_id)
    pack_num = orderLine.count()
    pack_sure_num = 0
    packObj = OrderLinePacking.objects.filter(order_id = order_id)
    for one in packObj:
        # 状态，0：无装箱指示，1：有装箱指示（分订单项指示）；2：统一指示
        if one.status !=0:
            pack_sure_num = pack_sure_num+1
    return pack_num,pack_sure_num

# 面辅料确认数目
def getClothSureNum(order_id):
    orderCloth = OrderCloth.objects.filter(order_id=order_id)
    order_cloth_num = orderCloth.count()
    order_cloth_sure_num = 0
    for one in orderCloth:
        if one.is_sure == 1:
            order_cloth_sure_num += 1
    return order_cloth_num, order_cloth_sure_num

# 面辅料入库数量
def getClothInStore(order_id):
    orderCloth = OrderCloth.objects.filter(order_id=order_id)
    order_cloth_store_num = orderCloth.count()
    order_cloth_store_sure_num = 0
    for one in orderCloth:
        if one.is_sure_in_store == 1:
            order_cloth_store_sure_num += 1
    return order_cloth_store_num, order_cloth_store_sure_num

# 成衣样品数量与确认
def getPlanSampleNum(order_id):
    orderObj = PlanOrder.objects.get(id=order_id)
    pclsObj = PlanClothSampleLine.objects.filter(plan_id=orderObj.plan_id)
    sample_num = pclsObj.count()
    sample_sure_num = 0
    for one in pclsObj:
        if one.is_sure ==1:
            sample_sure_num +=1
    return sample_num, sample_sure_num



# 日期之差
def downDay(d1,d2):
    if d1 and d2:
        dayNum = (d2.date()-d1.date()).days
    else:
        dayNum = None
    return dayNum
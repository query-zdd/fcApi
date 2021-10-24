# -*- coding:UTF-8 -*-
import logging
import types

import django
from django.db import models
from decimal import *

from django.db.models import Q
from django.db.models.base import ModelState
from datetime import datetime, date,timedelta

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

def getMakeFatoryInspect(order_id):
    bObj = FactoryMake.objects.filter(order_id=order_id,delete_time=None)
    mfi_num = bObj.count()
    mfi_y_num = 0
    for one in bObj:
        if one.inspect_name:
            mfi_y_num +=1
    return mfi_num,mfi_y_num

# 获取订单的所有的客户
def getAllCustom(order_id):
    order = PlanOrder.objects.get(id=order_id)
    orderLine = PlanOrderLine.objects.filter(order_id = order_id)
    orderClothLineShip = OrderClothLineShip.objects.filter(order_id=order_id)
    fkObj = FactoryMake.objects.filter(order_id = order_id)
    custom_list = []
    custom_dic = {}
    samp1 = []
    samp2 = []
    samp3 = []
    for one in orderLine:
        if one.order_custom not in custom_list:
            custom_list.append(one.order_custom)
        if one.order_custom not in samp1:
            samp1.append(one.order_custom)
    custom_dic['order_custom'] = order.custom
    custom_dic['line_order_custom'] = samp1

    for one1 in orderClothLineShip:
        if one1.delivery_name not in custom_list:
            custom_list.append(one1.delivery_name)
        if one1.delivery_name not in samp2:
            samp2.append(one1.delivery_name)
    custom_dic['list_delivery_name'] = samp2

    for one2 in fkObj:
        if one2.make_factory not in custom_list:
            custom_list.append(one2.make_factory)
        if one2.make_factory not in samp3:
            samp3.append(one2.make_factory)
    custom_dic['list_make_factory'] = samp3
    return custom_dic,custom_list

# 获取所有订单的支付信息
def orderPayStatus(order_id):
    order = PlanOrder.objects.get(id=order_id)
    if order.is_finish_pay == 1:
        orderLine = PlanOrderLine.objects.filter(delete_time=None, order_id=order_id)
        orderPay = OrderPay.objects.filter(delete_time=None, order_id=order_id)
        payInfo = OrderPayInfoList.objects.filter(delete_time=None, order_id=order_id)
        all_amount = Decimal(0)
        pay_amount = Decimal(0)
        for one in orderLine:
            try:
                if one.order_price:
                    all_amount += one.order_price
            except:
                pass
        for one1 in orderPay:
            try:
                if one1.amount:
                    all_amount += one1.amount
            except:
                pass
        for one2 in payInfo:
            try:
                if one2.pay_amount:
                    pay_amount += one2.pay_amount
            except:
                pass
        pay_finish_deg = round(pay_amount/all_amount,2)
        pay_status = 1
    else:
        orderLine = PlanOrderLine.objects.filter(delete_time=None,order_id=order_id)
        orderPay = OrderPay.objects.filter(delete_time=None,order_id = order_id)
        payInfo = OrderPayInfoList.objects.filter(delete_time=None,order_id = order_id)
        all_amount = Decimal(0)
        pay_amount = Decimal(0)
        for one in orderLine:
            try:
                if one.order_price:
                    all_amount +=one.order_price
            except:
                pass
        for one1 in orderPay:
            try:
                if one1.amount:
                    all_amount +=one1.amount
            except:
                pass
        for one2 in payInfo:
            try:
                if one2.pay_amount:
                    pay_amount +=one2.pay_amount
            except:
                pass
        if all_amount ==0:
            pay_finish_deg = 0
        else:
            pay_finish_deg =round(pay_amount/all_amount,2)
        pay_status = 0
    return pay_finish_deg,pay_status,all_amount,pay_amount


# 获取所有订单的未付款金额
def getOrderPayNum():
    order = PlanOrder.objects.filter(delete_time=None)
    order_num = order.count()
    order_no_pay_num = 0
    order_yes_pay_num = 0
    dollar_all = Decimal(0)
    euro_all = Decimal(0)
    renminbi_all = Decimal(0)
    dollar_y = Decimal(0)
    dollar_n = Decimal(0)
    euro_y = Decimal(0)
    euro_n = Decimal(0)
    renminbi_y = Decimal(0)
    renminbi_n = Decimal(0)
    for obj in order:
        if obj.is_finish_pay == 1:
            order_yes_pay_num +=1
        order_id = obj.id
        orderLine = PlanOrderLine.objects.filter(delete_time=None, order_id=order_id)
        orderPay = OrderPay.objects.filter(delete_time=None, order_id=order_id)
        payInfo = OrderPayInfoList.objects.filter(delete_time=None, order_id=order_id)
        for one in orderLine:
            try:
                if one.order_price:
                    if one.order_price_type == "美元":
                        dollar_all += one.order_price
                    if one.order_price_type == "欧元":
                        euro_all += one.order_price
                    if one.order_price_type == "人民币":
                        renminbi_all += one.order_price
            except:
                pass
        for one1 in orderPay:
            try:
                if one1.amount:
                    if one1.pay_type == "美元":
                        dollar_all += one1.amount
                    if one1.pay_type == "欧元":
                        euro_all += one1.amount
                    if one1.pay_type == "人民币":
                        renminbi_all += one1.amount
            except:
                pass
        for one2 in payInfo:
            try:
                if one2.pay_amount:
                    if one2.price_type == "美元":
                        dollar_y += one2.pay_amount
                    if one2.price_type == "欧元":
                        euro_y += one2.pay_amount
                    if one2.price_type == "人民币":
                        renminbi_y += one2.pay_amount
            except:
                pass
    order_no_pay_num = order_num - order_yes_pay_num
    dollar_n = dollar_all - dollar_y
    euro_n = euro_all - euro_y
    renminbi_n = renminbi_all - renminbi_y
    temp = {}
    temp['order_num'] = order_num
    temp['order_yes_pay_num'] = order_yes_pay_num
    temp['order_no_pay_num'] = order_no_pay_num
    temp['dollar_all'] = dollar_all
    temp['dollar_y'] = dollar_y
    temp['dollar_n'] = dollar_n
    temp['euro_all'] = euro_all
    temp['euro_y'] = euro_y
    temp['euro_n'] = euro_n
    temp['renminbi_all'] = renminbi_all
    temp['renminbi_y'] = renminbi_y
    temp['renminbi_n'] = renminbi_n
    return temp

def getSupplierSure(order_id):
    orderClothShip = OrderClothShip.objects.filter(delete_time=None, order_id=order_id)
    supplier_num = orderClothShip.count()
    supplier_sure_num = 0
    for one in orderClothShip:
        if one.is_sure_pay == 1:
            supplier_sure_num += 1
    supplier_no_num = supplier_num - supplier_sure_num
    return supplier_num,supplier_sure_num,supplier_no_num


# 获取指定订单，加工工厂，订单项下的产品的颜色，客户色号下的信息
def getOrderFactoryInfoColor(order_id,order_line_id,factory_make_id):

    order = PlanOrder.objects.get(id=order_id)
    orderLine = PlanOrderLine.objects.get(id = order_line_id)
    facObj = FactoryMake.objects.get(id=factory_make_id)
    fcLineObj = FactoryMakeLine.objects.filter(factory_make_id=factory_make_id,order_line_id = order_line_id,delete_time=None).order_by("color_name","specs")
    samp = []
    zemp = []
    jamp = {}
    specs_list =[]
    specs_dic = {}
    for one in fcLineObj:
        if one.color_name not in samp:
            samp.append(one.color_name)
            if jamp:
                jamp['specs_list'] = specs_dic
                zemp.append(jamp)
                jamp = {}
                specs_dic = {}
            # 检品出货详情
            mkfin = MakeFatoryInspect.objects.filter(order_line_id=order_line_id,make_factory_id=factory_make_id,color=one.color_num)
            jamp['order_line_id'] = order_line_id
            jamp['factory_make_id'] = factory_make_id
            # jamp['custom'] = orderLine.order_custom
            # jamp['order_type'] = orderLine.order_type
            jamp['color_name'] = one.color_name
            jamp['color_num'] = one.color_num
            if mkfin.count()>0:
                jamp['inspect_num'] = mkfin[0].inspect_num
                jamp['total'] = mkfin[0].total
                # B品数量
                jamp["inspect_b_num"] = mkfin[0].b_num

            else:
                jamp['inspect_num'] = 0
                jamp['total'] = 0
                jamp["inspect_b_num"] = 0
            jamp['sure_b_num'] = one.b_num
            specs_dic[one.specs] = one.specs
            
            #样品结算
            sample_pay_num = 0
            sample_num = 0
            planClothSamp = PlanClothSampleLine.objects.filter(plan_id=order.plan_id,custom= facObj.make_factory)
            if planClothSamp.count()>0:
                for one2 in planClothSamp:
                    planClothSampNum = PlanClothSampleNumber.objects.filter(pcsl_id = one2.id,sub_color_name= one.color_name)
                    for one3 in planClothSampNum:
                        sample_num +=one3.num
                        if one2.is_pay==1:
                            sample_pay_num +=one3.num
            jamp['sample_num'] = sample_num
            jamp['sample_pay_num'] = sample_pay_num
        else:
            specs_dic[one.specs] = one.specs

    return samp,zemp


#获取指定订单的生产应付
def getMakePayInfo1(nid):
    projectPay = ProductPayStatic.objects.get(id=nid, delete_time=None)
    one = OrderClothShip.objects.get(delete_time=None, id=nid)
    orderObj = PlanOrder.objects.get(id=projectPay.order_id)
    samp = {}
    planMater = PlanMaterial.objects.get(id=one.plan_material_id)
    samp['cloth_type'] = one.cloth_type
    samp['cloth_cat'] = one.cloth_cat
    samp['cloth_name'] = one.cloth_name
    samp['m_unit'] = planMater.m_unit
    samp['m_use'] = planMater.m_use
    samp['m_rate'] = planMater.m_rate
    samp['loss_lv'] = one.loss_lv
    samp['buy_all_num'] = one.buy_all_num
    samp['supplier'] = one.supplier
    samp['delivery_type'] = one.delivery_type
    samp['delivery_name'] = one.delivery_name
    if one.price_type:
        samp['price_type'] = one.price_type
    else:
        samp['price_type'] = "人民币"
    samp['all_amount'] = one.all_amount
    samp['is_inspect'] = one.is_inspect
    samp['order_cloth_ship_id'] = one.id
    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=one.order_cloth_id,
                                             order_cloth_ship_id=one.id).order_by('color', 'specs')
    sub_data = []
    for one1 in rObj:
        zamp = {}
        zamp["order_cloth_ship_line_id"] = one1.id
        zamp['color'] = one1.color
        zamp['color_num'] = one1.color_num
        zamp['guige'] = one1.guige
        zamp['specs'] = one1.specs
        zamp['order_num'] = orderObj.order_num
        zamp['buy_num'] = one1.buy_num

        zamp['provide_num'] = one1.provide_num
        zamp['provide_time'] = one1.provide_time
        zamp['price'] = one1.price
        zamp['sure_price'] = one1.sure_price
        zamp['amount'] = one1.amount
        zamp['sample_send_time'] = one1.sample_send_time
        zamp['is_sure_pay'] = one1.is_sure_pay
        sub_data.append(zamp)
    samp['sub_data'] = sub_data
    productInfo = ProductPayInfo.objects.filter(product_pay_static_id=nid)
    samp['pay_info'] = productInfo.values()
    return  samp


#获取指定订单的生产应付
def getMakePayInfo2(nid):
    projectPay = ProductPayStatic.objects.get(id=nid, delete_time=None)
    facObj = FactoryMake.objects.get(id = projectPay.factory_make_id)
    facinObj = MakeFatoryInspect.objects.filter(make_factory_id=projectPay.factory_make_id)
    order = PlanOrder.objects.get(id =projectPay.order_id )
    paln = PlanPrice.objects.get(plan_id = order.plan_id)
    inspect_num = 0
    b_num = 0
    for one in facinObj:
        if one.inspect_num:
            inspect_num +=one.inspect_num
        if b_num:
            b_num +=one.b_num
    samp={ }
    samp['pay_project'] = "加工费"
    samp['custom'] = facObj.make_factory
    samp['price_type'] = projectPay.price_type
    samp['plan_amount'] = paln.plan_price
    samp['inspect_num'] = inspect_num
    if facObj.make_num:
        samp['good_num'] = facObj.make_num - b_num
    else:
        samp['good_num'] = 0
    samp['b_num'] = b_num
    try:
        samp['b_lv'] = b_num/ samp['good_num']
    except:
        samp['b_lv'] = 0
    samp['pay_rule'] = "结算原则"
    samp['pay_amount'] = facObj.amount
    productInfo = ProductPayInfo.objects.filter(product_pay_static_id=nid)
    samp['pay_info'] = productInfo.values()
    return  samp


#获取指定订单的生产应付
def getMakePayInfo3(nid):
    projectPay = ProductPayStatic.objects.get(id=nid, delete_time=None)
    samp = model_to_dict(projectPay)
    productInfo = ProductPayInfo.objects.filter(product_pay_static_id=nid)
    samp['pay_info'] = productInfo.values()
    return  samp

# 获取订单所有的其他报价
def getOrderOtherFee(order_id):
    order = PlanOrder.objects.get(id=order_id)
    orderPay = OrderPay.objects.filter(delete_time=None,order_id = order_id)
    productPay = ProductPayStatic.objects.filter(order_id = order_id)
    samplePay = SamplePayStatic.objects.filter(order_id = order_id)
    samp = []
    other_num = orderPay.count()+productPay.count()+samplePay.count()
    other_fee_num = 0
    for one in orderPay:
        temp = {}
        temp['other_type'] = 1
        temp['other_id'] = one.id
        temp['pay_project'] = "订单应收其他账目"
        temp['custom'] =one.provide_custom
        temp['price_type'] = one.pay_type
        temp['pay_amount'] = one.amount
        temp['pay_num'] = one.pay_num
        temp['finish_amount'] = one.amount
        temp['pay_custom'] = one.custom
        if one.fee_no:
            fee_no = one.fee_no.split("|")
        else:
            fee_no = []
        if one.fee_amount:
            amount = one.fee_amount.split("|")
        else:
            amount = []
        if one.file_url:
            file_url = one.file_url.split("|")
        else:
            file_url = []
        file_url_y = []
        fee_no_y = []
        amount_y = []
        for l1 in fee_no:
            if l1:
                fee_no_y.append(l1)
        for l2 in amount:
            if l2:
                amount_y.append(Decimal(l2))
        for l3 in file_url:
            if l3:
                file_url_y.append(Decimal(l2))
        temp['fee_no'] = fee_no_y
        temp['fee_amount'] = amount_y
        temp['file_url'] = file_url_y
        temp['fee_no_status'] = one.fee_no_status
        if one.fee_amount:
            other_fee_num +=1
        samp.append(temp)
    for one1 in productPay:
        temp = {}
        temp['other_type'] = 2
        temp['pay_project'] = one1.pay_project
        temp['custom'] = one1.custom
        temp['price_type'] = one1.price_type
        temp['pay_amount'] = one1.pay_amount
        temp['pay_num'] = one1.pay_num
        temp['finish_amount'] = one1.pay_amount
        temp['pay_custom'] = one1.pay_custom
        if one1.fee_no:
            fee_no = one1.fee_no.split("|")
        else:
            fee_no = []
        if one1.fee_amount:
            amount = one1.fee_amount.split("|")
        else:
            amount = []
        if one1.file_url:
            file_url = one1.file_url.split("|")
        else:
            file_url = []

        file_url_y = []
        fee_no_y = []
        amount_y = []
        for l1 in fee_no:
            if l1:
                fee_no_y.append(l1)
        for l2 in amount:
            if l2:
                amount_y.append(Decimal(l2))
        for l3 in file_url:
            if l3:
                file_url_y.append(Decimal(l2))
        temp['fee_no'] = fee_no_y
        temp['fee_amount'] = amount_y
        temp['file_url'] = file_url_y
        temp['fee_no_status'] = one1.fee_no_status
        if one1.fee_amount:
            other_fee_num +=1
        samp.append(temp)
    for one2 in samplePay:
        temp = {}
        temp['other_type'] = 3
        temp['other_id'] = one2.id
        temp['pay_project'] ="成衣其他应付账目"
        temp['custom'] = one2.custom
        temp['price_type'] = one2.price_type
        temp['pay_amount'] = one2.pay_amount
        temp['pay_num'] = one2.pay_num
        temp['finish_amount'] = one2.finish_amount
        temp['pay_custom'] = one2.pay_custom
        if one2.fee_no:
            fee_no = one2.fee_no.split("|")
        else:
            fee_no = []
        if one2.fee_amount:
            amount = one2.fee_amount.split("|")
        else:
            amount = []
        if one2.file_url:
            file_url = one2.file_url.split("|")
        else:
            file_url = []
        file_url_y = []
        fee_no_y = []
        amount_y = []
        for l1 in fee_no:
            if l1:
                fee_no_y.append(l1)
        for l2 in amount:
            if l2:
                amount_y.append(Decimal(l2))
        for l3 in file_url:
            if l3:
                file_url_y.append(Decimal(l2))
        temp['fee_no'] = fee_no_y
        temp['fee_amount'] = amount_y
        temp['file_url'] = file_url_y
        temp['fee_no_status'] = one2.fee_no_status
        if one2.fee_amount:
            other_fee_num +=1
        samp.append(temp)
    return samp,other_num,other_fee_num

# 日期之差
def downDay(d1,d2):
    if d1 and d2:
        dayNum = (d2.date()-d1.date()).days
    else:
        dayNum = None
    return dayNum

def getInSn(sn):
    num = len(sn)
    result = []
    for i in range(num):
        result.append(sn)
        sn = sn[:-1]
    return result

def checkPermission(request):
    url = request.get_full_path()
    try:
        token = request.META.get("HTTP_AUTHORIZATION","")
        sn = request.META.get("HTTP_AUTHSN", "")
        result = getInSn(sn)
        if not token:
            msg = "未登录，请先登录系统"
            return False,msg
        else:
            td = datetime.now()-timedelta(seconds=3600)
            tObj = ZToken.objects.filter(token=token,create_time__gt=td)
            if tObj.count()>0:
                userObj = RoleMenu.objects.get(id=tObj[0].type)
                role = Role.objects.get(id=userObj.role_id)
                ach_list = role.authority_list
                flag = False
                msg = "当前账户无此权限！"
                for s_num in result:
                    if s_num in ach_list:
                        flag = True
                        msg = "权限通过"
                return flag,msg
            else:
                msg = "token已经过期，请重新登录！"
                return False, msg
    except:
        msg = "系统繁忙！"
        return False, msg

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

def getOverflow(order_id):
    orderLine = PlanOrderLine.objects.filter(order_id=order_id)
    short_overflow_num = 0
    contract_num = 0
    for one in orderLine:
        short_overflow_num +=(one.order_num  - one.contract_num)
        contract_num += one.contract_num
    short_overflow =round(short_overflow_num/contract_num,2)
    return short_overflow_num,short_overflow



# 日期之差
def downDay(d1,d2):
    if d1 and d2:
        dayNum = (d2.date()-d1.date()).days
    else:
        dayNum = None
    return dayNum
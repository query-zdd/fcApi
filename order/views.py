from django.http import HttpResponse,request
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from datetime import *

from lin.utils import *
from secure.from_safe import *
from lin.models import *
from lin.exception import Error
from secure.upload.upload_image.config import  access_key,secret_key,base_url
from secure.serializers import zddpaginate
import math
from order.utils import *
from django.db.models import Sum
# Create your views here.
############################订单管理-出货方案###############################################

class showOutStockView(APIView):
    # 添加/编辑 订单出货方案
    @csrf_exempt
    def post(self, request):
        sn = "201"
        ret, msg = checkPermission(request,sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = orderOutstockSerializer(data=request.data)
        if valObj.is_valid():
            dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ''
            #################校验数据################################
            d_flag = 0
            d_num = 0
            contact_ids = []
            del_out_id=[]
            contact_info={}
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderOutstockLineSerializer(data=done)
                try:
                    if int(done["id"])==0:
                        order_one_lv = (100 + int(done["short_overflow"]) + int(done['short_overflow_direct']))/ 100
                        str_key = "k" + str(done['order_line_id'])
                        num_str_key = "num" + str(done['order_line_id'])
                        lv_str_key = "lvm" + str(done['order_line_id'])
                        if done['order_line_id'] not in contact_ids:
                            contact_ids.append(done['order_line_id'])
                            # 合同数量
                            contact_info[str_key] = done['contract_num']
                            # 下单数量=合同数量+短溢装数量（合同短溢装+指示短溢装）
                            contact_info[num_str_key] = done['order_num']
                            contact_info[lv_str_key] = order_one_lv
                        else:
                            contact_info[str_key] += done['contract_num']
                            contact_info[num_str_key] += done['order_num']
                            contact_info[lv_str_key] = order_one_lv
                    else:
                        order_one_lv = (100 + done["short_overflow"] + int(done['short_overflow_direct'])) / 100
                        str_key = "k" + str(done['order_line_id'])
                        num_str_key = "num" + str(done['order_line_id'])
                        lv_str_key = "lvm" + str(done['order_line_id'])
                        if done['order_line_id'] not in contact_ids:
                            contact_ids.append(done['order_line_id'])
                            # 合同数量
                            contact_info[str_key] = done['contract_num']
                            # 下单数量=合同数量+短溢装数量（合同短溢装+指示短溢装）
                            contact_info[num_str_key] = done['order_num']
                            contact_info[lv_str_key] = order_one_lv
                        else:
                            contact_info[str_key] += done['contract_num']
                            contact_info[num_str_key] += done['order_num']
                            contact_info[lv_str_key] = order_one_lv
                        if done['id'] not in del_out_id:
                            del_out_id.append(done['id'])
                except:
                    pass
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            for k_id in contact_ids:
                orderlineObj = PlanOrderLine.objects.get(id=k_id)
                outall = OutStock.objects.filter(~Q(id__in=del_out_id),order_line_id=k_id)
                str_key = "k"+str(k_id)
                num_str_key = "num" +str(k_id)
                lv_str_key = "lvm" + str(k_id)
                for o in outall:
                    contact_info[str_key] += o.contract_num
                    contact_info[num_str_key] +=o.order_num
                if orderlineObj.contract_num!=contact_info[str_key]:
                    msg = "合同数量不一致"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)

            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OutStock.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = OutStock()
                                bObj.create_time = dt
                        except:
                            bObj = OutStock()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        bObj.order_line_id = done['order_line_id']
                        bObj.color = done['color']
                        bObj.color_name = done['color_name']
                        bObj.color_num = done['color_num']
                        bObj.specs = done['specs']
                        bObj.contract_num = done['contract_num']
                        bObj.short_overflow = done['short_overflow']
                        bObj.short_overflow_direct = int(done['short_overflow_direct'])
                        bObj.order_num = math.ceil(done['order_num'])
                        bObj.save()
                        # 更新orderline
                        num_str_key = "num" + str(done['order_line_id'])
                        orderline = PlanOrderLine.objects.get(id=done['order_line_id'])
                        orderline.is_pushprogram = 1
                        if int(done["id"])==0:
                            orderline.order_num = contact_info[num_str_key]
                        orderline.short_overflow_direct = int(done['short_overflow_direct'])
                        orderline.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    pgall = PlanOrderLine.objects.filter(order_id=data['order_id'],delete_time=None)
                    pgone = PlanOrderLine.objects.filter(order_id=data['order_id'],is_pushprogram=1,delete_time=None)
                    if pgall.count()==pgone.count():
                        order.is_pushprogram = 1
                    order.pushprogram_num =pgone.count()
                    o_order_num = 0
                    for pgone_num in pgone:
                        o_order_num +=pgone_num.order_num
                    order.order_num = o_order_num
                    if dhkhao:
                        order.dhkhao = dhkhao
                    order.save()
                except:
                    pass
                msg = "创建/编辑出货方案成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 订单出货方案showOutStock
    @csrf_exempt
    def delete(self, request):
        sn = "201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = OutStock.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "出货方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "出货方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class showOutStockOneView(APIView):
    # 单个删除 订单出货方案
    @csrf_exempt
    def delete(self, request, nid):
        sn = "201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            valObj = orderOutstockDeleteOneSerializer(data=request.query_params)
            if valObj.is_valid():
                order_line_id = valObj.data['order_line_id'] if valObj.data['order_line_id'] is not None else 0
                color = valObj.data['color'] if valObj.data['color'] is not None else ""
                specs = valObj.data['specs'] if valObj.data['specs'] is not None else ""
                flag = 1
                bObj =OutStock.objects.filter(delete_time=None)
                if order_line_id:
                    bObj = bObj.filter(order_line_id=order_line_id)
                    flag = 0
                if color:
                    bObj = bObj.filter(color=color)
                    flag = 0
                if specs:
                    bObj = bObj.filter(specs=specs)
                    flag = 0
                if flag:
                    bObj = []
                for one in bObj:
                    dt = datetime.now()
                    one.delete_time = dt
                    one.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "出货方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "出货方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取订单 订单出货方案
    @csrf_exempt
    def get(self, request, nid):
        sn = "201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                samplist = []
                if sort_type:
                    jamp = {}
                    rObj = OutStock.objects.filter(delete_time=None,order_id=nid).order_by('color','specs')
                    samplist = rObj.values()

                else:
                    short_overflow_num = 0
                    orderline = PlanOrderLine.objects.filter(delete_time=None,order_id=nid)
                    samplist=[]
                    for one in orderline:
                        samp={}
                        samp['order_custom'] = one.order_custom
                        samp['order_type'] = one.order_type
                        samp['contract_num'] = one.contract_num
                        samp['order_line_id'] = one.id
                        rObj = OutStock.objects.filter(delete_time=None, order_line_id=one.id).order_by('color', 'specs')
                        if rObj.count()>0:
                            samp['out_stock'] = rObj.values()
                            for one in rObj:
                                if one.order_num and one.contract_num:
                                    short_overflow_num += one.order_num - one.contract_num
                        else:
                            samp['out_stock'] = []
                            samp['short_overflow'] = one.short_overflow
                        samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                orderObj = PlanOrder.objects.get(id=nid)
                temp['orderObj'] = model_to_dict(orderObj)
                temp['short_overflow_num'] = short_overflow_num
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的出货方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



############################订单管理-录入工厂方案###############################################

class factoryMakeView(APIView):
    # 添加/编辑 录入工厂方案
    @csrf_exempt
    def post(self, request):
        sn = "202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = factoryMakeSerializer(data=request.data)
        if valObj.is_valid():
            dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = factoryMakeLineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0:
                for done in dataone:
                    valObjline = factoryMakeLineSerializer(data=done)
                    flag = valObjline.is_valid()
                    make_time = valObjline.data['make_time'] if valObjline.data['make_time'] is not None else ""
                    make_factory = valObjline.data['make_factory'] if valObjline.data['make_factory'] is not None else ""
                    coop_mode = valObjline.data['coop_mode'] if valObjline.data['coop_mode'] is not None else ""
                    inspect_company = valObjline.data['inspect_company'] if valObjline.data['inspect_company'] is not None else ""
                    order_admin = valObjline.data['order_admin'] if valObjline.data['order_admin'] is not None else ""
                    ticketing_custom = valObjline.data['ticketing_custom'] if valObjline.data['ticketing_custom'] is not None else ""
                    subline = done["subline"]
                    try:
                        try:
                            mid = done["factory_make_id"]
                            if mid:
                                bObj = FactoryMake.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = FactoryMake()
                                bObj.create_time = dt
                        except:
                            bObj = FactoryMake()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        if make_time:
                            bObj.make_time = make_time
                        bObj.make_factory = make_factory
                        bObj.coop_mode = coop_mode
                        bObj.inspect_company = inspect_company
                        bObj.order_admin = order_admin
                        bObj.ticketing_custom = ticketing_custom
                        bObj.flag = 1
                        bObj.save()
                        if mid:
                            factory_make_id = mid
                        else:
                            fmObj = FactoryMake.objects.latest('id')
                            factory_make_id = fmObj.id
                        for one in subline:
                            try:
                                mlid = one
                                if mlid:
                                    blObj = FactoryMakeLine.objects.get(id=one)
                                    blObj.update_time = dt
                                else:
                                    blObj = FactoryMakeLine()
                                    blObj.create_time = dt

                            except:
                                blObj = FactoryMakeLine()
                                blObj.create_time = dt
                            blObj.factory_make_id = factory_make_id
                            # try:
                            #     blObj.color = one['color']
                            #     blObj.color_name = one['color_name']
                            #     blObj.color_num = one['color_num']
                            #     blObj.specs = one['specs']
                            #     blObj.contract_num = one['contract_num']
                            #     blObj.short_overflow = one['short_overflow']
                            #     blObj.short_overflow_direct = one['short_overflow_direct']
                            #     blObj.order_num = one['order_num']
                            #     blObj.make_num = one['make_num']
                            #     blObj.order_id = data['order_id']
                            #     blObj.order_line_id = one['order_line_id']
                            # except:
                            #     pass
                            blObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.work_type =data['work_type']
                    if dhkhao:
                        order.dhkhao = dhkhao
                    order.save()
                except:
                    pass
                factory_make_id =factory_make_id
                msg = "创建/编辑工厂方案成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                    "factory_make_id":factory_make_id,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 录入工厂方案
    @csrf_exempt
    def delete(self, request):
        sn = "202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = FactoryMake.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
                subObj = FactoryMakeLine.objects.filter(factory_make_id=nid)
                for one in subObj:
                    dt = datetime.now()
                    one.delete_time = dt
                    one.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "工厂方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "出货方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class factoryMakeOneView(APIView):
    # 获取订单 录入工厂方案
    @csrf_exempt
    def get(self, request, nid):
        sn = "202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                # 删除垃圾数据
                try:
                    xfmObj  = FactoryMake.objects.filter(flag=0)
                    for one in xfmObj:
                        xfmlObj = FactoryMakeLine.objects.filter(factory_make_id=one.id)
                        for onesub in xfmlObj:
                            onesub.delete()
                        one.delete()
                except:
                    pass
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                samplist = []
                fmObj = FactoryMake.objects.filter(delete_time=None, order_id=nid, flag=1)
                orderObj = PlanOrder.objects.get(id=nid)
                orderLineObj = PlanOrderLine.objects.filter(order_id=nid)
                samplist=[]
                for one in fmObj:
                    samp={}
                    samp['make_time'] = one.make_time
                    samp['make_factory'] = one.make_factory
                    samp['coop_mode'] = one.coop_mode
                    samp['inspect_company'] = one.inspect_company
                    samp['order_admin'] = one.order_admin
                    samp['ticketing_custom'] = one.ticketing_custom
                    samp['factory_make_id'] = one.id
                    rObj = FactoryMakeLine.objects.filter(delete_time=None, factory_make_id=one.id).order_by('color', 'specs')
                    samp['subline'] = rObj.values()
                    samplist.append(samp)
                temp = {}
                short_overflow_num = 0
                outobj = OutStock.objects.filter(delete_time=None,order_id = nid)
                for one in outobj:
                    short_overflow_num +=one.order_num-one.contract_num
                temp["data"] = samplist
                temp['work_type'] = orderObj.work_type
                temp['contract_num'] = orderObj.contract_num
                temp['order_num'] = orderObj.order_num
                temp['short_overflow_num'] = short_overflow_num
                temp['inspect_company'] = orderLineObj[0].inspect_company
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的出货方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理---加工方案############################################
class machiningView(APIView):
    # 添加/编辑 加工方案
    @csrf_exempt
    def post(self, request):
        sn = "202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = machiningSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = machiningLineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            factory_make_id = valObj.data['factory_make_id'] if valObj.data['factory_make_id'] is not None else 0
            dt = datetime.now()
            # 如果没有factory_make_id新建factory_make
            if not factory_make_id:
                fmObj  = FactoryMake()
                fmObj.flag = 0
                fmObj.create_time = dt
                fmObj.save()
                fmone = FactoryMake.objects.latest('id')
                factory_make_id = fmone.id
            dt = datetime.now()
            subline = []
            ##############保存出货方案#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            no_allocation_num = done['no_allocation_num'] if done['no_allocation_num'] is not None else 0
                        except:
                            no_allocation_num = 0
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = FactoryMakeLine.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = FactoryMakeLine()
                                bObj.create_time = dt

                        except:
                            bObj = FactoryMakeLine()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        bObj.order_line_id = data['order_line_id']
                        bObj.color = done['color']
                        bObj.color_name = done['color_name']
                        bObj.color_num = done['color_num']
                        bObj.specs = done['specs']
                        bObj.contract_num = done['contract_num']
                        bObj.short_overflow = data['short_overflow']
                        bObj.short_overflow_direct = data['short_overflow_direct']
                        bObj.order_num = done['order_num']
                        bObj.make_num = done['make_num']
                        bObj.factory_make_id = factory_make_id
                        bObj.no_allocation_num = no_allocation_num
                        bObj.save()
                        # 修改其他方案的未分配数量
                        fcObj = FactoryMakeLine.objects.filter(delete_time=None,order_line_id=data['order_line_id'],color=done['color'],specs=done['specs'])
                        for one in fcObj:
                            one.no_allocation_num = no_allocation_num
                            one.save()
                        if mid:
                            subline.append(mid)
                        else:
                            fmObj = FactoryMakeLine.objects.latest('id')
                            subline.append(fmObj.id)
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新orderline
                    orderline = PlanOrderLine.objects.get(id=data['order_line_id'])
                    orderline.is_work_progrem =1
                    orderline.save()
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.is_workprogram = 1
                    pg_num = PlanOrderLine.objects.filter(order_id=data['order_id'], is_work_progrem=1).count()
                    order.workprogram_num = pg_num
                    order.save()
                except:
                    pass
                msg = "创建/编辑出货方案成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                    "subline":subline,
                    "factory_make_id":factory_make_id,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class machiningOneView(APIView):
    # 获取订单 加工方案
    @csrf_exempt
    def get(self, request, nid):
        sn = "202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = machiningGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                order = PlanOrder.objects.get(id = nid)
                orderline = PlanOrderLine.objects.filter(delete_time=None,order_id=nid)
                factory_make_id = valObj.data['id'] if valObj.data['id'] is not None else 0
                samplist=[]
                for one in orderline:
                    samp={}
                    samp['order_custom'] = one.order_custom
                    samp['order_type'] = one.order_type
                    samp['order_line_id'] = one.id
                    rObj = FactoryMakeLine.objects.filter(delete_time=None, order_line_id=one.id,factory_make_id=factory_make_id).order_by('color', 'specs')
                    if rObj.count()>0:
                        samp['machining_sub'] = rObj.values()
                    else:
                        rOne =OutStock.objects.filter(delete_time=None,order_id=nid,order_line_id=one.id).order_by('color','specs')
                        rOut =  rOne.values()
                        for obj in rOut:
                            fcObj = FactoryMakeLine.objects.filter(delete_time=None, order_line_id=one.id,color=obj['color'],specs=obj['specs'])
                            order_num = obj['order_num']
                            make_num = 0
                            for o in fcObj:
                                make_num = make_num + o.make_num
                            obj['no_allocation_num'] = order_num - make_num
                            obj['make_num'] = 0
                            obj['out_id'] = obj['id']
                            obj['id'] = 0
                        samp['machining_sub'] = rOut

                    samplist.append(samp)

                temp = {}
                temp['work_type'] = order.work_type
                temp["data"] = samplist
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的出货方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



############################订单管理-面辅料采购###############################################

class orderClothView(APIView):
    # 添加/编辑 面辅料采购
    @csrf_exempt
    def post(self, request):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = orderClothSerializer(data=request.data)
        if valObj.is_valid():
            work_type = valObj.data['work_type'] if valObj.data['work_type'] is not None else ""
            dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderClothLineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
                subdata = done['sub_data']
                s_flag = 0
                s_num = 0
                for sdone in subdata:
                    s_num = s_num + 1
                    valObjline = orderClothLineSubSerializer(data=sdone)
                    if not valObjline.is_valid():
                        s_flag = 1
                        samp = {}
                        samp['msg'] = valObjline.errors
                        samp['key_num'] = s_num
                        l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0 and s_flag == 0:
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderCloth.objects.get(id=mid)
                                bObj.update_time = dt
                                # #编辑时，删除已有的sku数据
                                # nbObj = OrderClothShip.objects.filter(order_cloth_id=mid)
                                # for one in nbObj:
                                #     nbObjline = OrderClothLineShip.objects.filter(order_cloth_id=mid)
                                #     for sub in nbObjline:
                                #         sub.delete()
                                #         sub.save()
                                #     one.delete()
                                #     one.save()
                            else:
                                bObj = OrderCloth()
                                bObj.create_time = dt
                        except:
                            bObj = OrderCloth()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        bObj.plan_id = data['plan_id']
                        bObj.plan_material_id = done['plan_material_id']
                        bObj.cloth_type = done['cloth_type']
                        bObj.cloth_cat = done['cloth_cat']
                        bObj.cloth_name = done['cloth_name']
                        bObj.delivery_type = done['delivery_type']
                        bObj.delivery_name = done['delivery_name']
                        try:
                            bObj.is_inspect = done['is_inspect']
                        except:
                            bObj.is_inspect = 0
                        bObj.buy_all_num = done['buy_all_num']
                        bObj.loss_lv = done['loss_lv']
                        bObj.save()
                        if mid:
                            order_cloth_id = mid
                        else:
                            ocOne = OrderCloth.objects.latest("id")
                            order_cloth_id = ocOne.id
                        # 保存发货方案
                        try:
                            if not mid:
                                nbObj = OrderClothShip()
                                planmObj = PlanMaterial.objects.filter(id=done['plan_material_id'], delete_time=None)
                                if planmObj.count() > 0:
                                    nbObj.supplier = planmObj[0].complayer
                                nbObj.plan_material_id = done['plan_material_id']
                                nbObj.create_time = dt
                                nbObj.order_id = data['order_id']
                                nbObj.plan_id = data['plan_id']
                                nbObj.cloth_type = done['cloth_type']
                                nbObj.cloth_cat = done['cloth_cat']
                                nbObj.cloth_name = done['cloth_name']
                                nbObj.delivery_type = done['delivery_type']
                                nbObj.delivery_name = done['delivery_name']
                                try:
                                    nbObj.is_inspect = done['is_inspect']
                                except:
                                    nbObj.is_inspect = 0
                                nbObj.buy_all_num = done['buy_all_num']
                                nbObj.loss_lv = done['loss_lv']
                                nbObj.order_cloth_id = order_cloth_id
                                nbObj.save()
                            if mid:
                                ocsObj = OrderClothShip.objects.filter(order_cloth_id=mid)
                                for ocs in ocsObj:
                                    planmObj = PlanMaterial.objects.filter(id=done['plan_material_id'],
                                                                           delete_time=None)
                                    if planmObj.count() > 0:
                                        ocs.supplier = planmObj[0].complayer
                                    ocs.plan_material_id = done['plan_material_id']
                                    ocs.create_time = dt
                                    ocs.order_id = data['order_id']
                                    ocs.plan_id = data['plan_id']
                                    ocs.cloth_type = done['cloth_type']
                                    ocs.cloth_cat = done['cloth_cat']
                                    ocs.cloth_name = done['cloth_name']
                                    try:
                                        ocs.is_inspect = done['is_inspect']
                                    except:
                                        ocs.is_inspect = 0
                                    ocs.buy_all_num = done['buy_all_num']
                                    ocs.loss_lv = done['loss_lv']
                                    ocs.save()
                        except:
                            pass
                        # 保存面辅料的sku
                        subdata = done['sub_data']
                        for sub in subdata:
                            try:
                                s_id = sub["id"]
                                if s_id:
                                    sbObj = OrderClothLine.objects.get(id=s_id)
                                    sbObj.update_time = dt
                                else:
                                    sbObj = OrderClothLine()
                                    sbObj.create_time = dt
                            except:
                                sbObj = OrderClothLine()
                                sbObj.create_time = dt
                            sbObj.order_id = data['order_id']
                            sbObj.order_cloth_id = order_cloth_id
                            if done['cloth_type'] ==4:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                                sbObj.specs = sub['specs']
                                outStackObj = OutStock.objects.filter(order_id=data['order_id'],color=sub['color'],
                                                                      color_num=sub['color_num'],specs=sub['specs'])
                                order_num=0
                                for one in outStackObj:
                                    order_num +=one.order_num
                                sbObj.order_num =order_num
                            if done['cloth_type'] ==3:
                                sbObj.specs = sub['specs']
                                outStackObj = OutStock.objects.filter(order_id=data['order_id'], specs=sub['specs'])
                                order_num = 0
                                for one in outStackObj:
                                    order_num += one.order_num
                                sbObj.order_num = order_num
                            if done['cloth_type'] ==2:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                                outStackObj = OutStock.objects.filter(order_id=data['order_id'], color=sub['color'],
                                                                      color_num=sub['color_num'])
                                order_num = 0
                                for one in outStackObj:
                                    order_num += one.order_num
                                sbObj.order_num = order_num
                            if done['cloth_type'] ==1:
                                orderOne = PlanOrder.objects.get(id=data['order_id'])
                                sbObj.order_num = orderOne.order_num
                            sbObj.guige = sub['guige']
                            sbObj.buy_num = sub['buy_num']
                            sbObj.is_inspect = sub['is_inspect']
                            sbObj.save()
                            if s_id:
                                order_cloth_line_id = s_id
                            else:
                                ocOne = OrderClothLine.objects.latest("id")
                                order_cloth_line_id = ocOne.id
                            #保存发货方案的sku
                            if not mid:
                                ncOne = OrderClothShip.objects.latest("id")
                                try:
                                    nblObj = OrderClothLineShip()
                                    nblObj.create_time = dt
                                    nblObj.order_id = data['order_id']
                                    nblObj.order_cloth_id = order_cloth_id
                                    if done['cloth_type'] == 4:
                                        nblObj.color = sub['color']
                                        nblObj.color_num = sub['color_num']
                                        nblObj.specs = sub['specs']
                                    if done['cloth_type'] == 3:
                                        nblObj.specs = sub['specs']
                                    if done['cloth_type'] == 2:
                                        nblObj.color = sub['color']
                                        nblObj.color_num = sub['color_num']
                                    nblObj.guige = sub['guige']
                                    nblObj.buy_num = sub['buy_num']
                                    nblObj.order_cloth_line_id =order_cloth_line_id
                                    nblObj.order_cloth_ship_id =ncOne.id
                                    if planmObj.count() > 0:
                                        nblObj.price = planmObj[0].price
                                        nblObj.amount = planmObj[0].total
                                    nblObj.save()
                                except:
                                    pass
                            if mid:
                                if s_id:
                                    ocslObj = OrderClothLineShip.objects.filter(order_cloth_line_id=s_id,order_cloth_id=order_cloth_id)
                                    for ocsl in ocslObj:
                                        ocsl.buy_num = sub['buy_num']
                                        ocsl.guige = sub['guige']
                                        ocsl.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.is_buyprogram =1
                    bg_num = OrderCloth.objects.filter(order_id=data['order_id'],delete_time=None).count()
                    order.buyprogram_num =bg_num
                    if dhkhao:
                        order.dhkhao = dhkhao
                    if work_type:
                        order.work_type = work_type
                    order.save()
                except:
                    pass
                msg = "创建/编辑面辅料采购"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 面辅料采购
    @csrf_exempt
    def delete(self, request):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = OrderCloth.objects.get(id=nid)
                dt = datetime.now()
                subObj = OrderClothLine.objects.filter(order_cloth_id=bObj.id)
                for one in subObj:
                    one.delete_time = dt
                    one.save()
                sbObj = OrderClothShip.objects.filter(order_cloth_id=nid)
                for one1 in sbObj:
                    one1.delete_time = dt
                    one1.save()
                subsbObj = OrderClothLineShip.objects.filter(order_cloth_id=nid)
                for one2 in subsbObj:
                    one2.delete_time = dt
                    one2.save()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "出货方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class orderClothOneView(APIView):
    # 获取订单 面辅料采购
    @csrf_exempt
    def get(self, request, nid):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
                orderCloth = OrderCloth.objects.filter(delete_time=None,order_id=nid)
                planObj = Plan.objects.get(id=orderObj.plan_id)
                fmObj = FactoryMake.objects.filter(order_id=nid)
                coop_mode = ''
                ticketing_custom = ''
                make_factory = []
                for o in fmObj:
                    make_factory.append(o.make_factory)
                    coop_mode +=o.coop_mode+'|'
                    ticketing_custom +=o.ticketing_custom+'|'
                samplist=[]
                order_cloth_num_sure = 0
                for one in orderCloth:
                    if one.is_sure_in_store == 1:
                        order_cloth_num_sure +=1
                    samp={}
                    samp['plan_material_id'] = one.plan_material_id
                    planmobj = PlanMaterial.objects.get(id=one.plan_material_id)
                    samp['is_finish'] = planmobj.is_finish
                    samp['cloth_type'] = one.cloth_type
                    samp['cloth_cat'] = one.cloth_cat
                    samp['cloth_name'] = one.cloth_name
                    samp['delivery_type'] = one.delivery_type
                    samp['delivery_name'] = one.delivery_name
                    samp['is_inspect'] = one.is_inspect
                    samp['buy_all_num'] = one.buy_all_num
                    samp['loss_lv'] = one.loss_lv
                    samp['order_cloth_id'] = one.id
                    rObj = OrderClothLine.objects.filter(delete_time=None, order_cloth_id=one.id).order_by('color', 'specs')
                    rObjList = rObj.values()
                    for one1 in rObjList:
                        one1["order_cloth_line_id"] = one1["id"]
                        # if one1['is_inspect']:
                        #     one1["is_inspect"] = one.is_inspect
                        del one1["id"]
                    samp['sub_data'] = rObjList
                    samplist.append(samp)
                # 备注
                orderline = PlanOrderLine.objects.filter(delete_time=None, order_id=nid)
                comments = ""
                for po1 in orderline:
                    if po1.comments:
                        comments += po1.comments
                # 注意事项
                notes_all_num, notes_sure_num = getNotesNum(plan_id=orderObj.plan_id)
                temp = {}
                temp["data"] = samplist
                temp["orderObj"] = model_to_dict(orderObj)
                temp['coop_mode'] = coop_mode
                temp['ticketing_custom'] = ticketing_custom
                temp['order_cloth_num'] = orderCloth.count()
                temp['order_cloth_num_sure'] = order_cloth_num_sure
                temp['order_cloth_num_no'] = orderCloth.count()-order_cloth_num_sure
                temp['make_factory'] = make_factory
                temp['comments'] = comments
                temp['notes_all_num'] = notes_all_num
                temp['notes_sure_num'] = notes_sure_num
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的面辅料采购信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################订单管理-注意事项###############################################

class orderNotesView(APIView):
    # 添加/编辑 注意事项
    @csrf_exempt
    def post(self, request):
        sn = "2040102,2040202,1010210,30101,30201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = orderNotesSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            order_id = valObj.data['order_id'] if valObj.data['order_id'] is not None else 0
            dataone = data['data']
            dt = datetime.now()
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderNotesLineSerializer(data=done)
                if not valObjline.is_valid():
                    msg = valObjline.errors
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
                if valObjline.is_valid():
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderNotes.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                if valObjline.data['notes_id']:
                                    bList = OrderNotes.objects.filter(plan_id=valObj.data['plan_id'],notes_id=valObjline.data['notes_id'])
                                    if bList.count()>0:
                                        bObj = bList[0]
                                        bObj.update_time = dt
                                    else:
                                        bObj = OrderNotes()
                                        bObj.create_time = dt
                        except:
                            bObj = OrderNotes()
                            bObj.create_time = dt
                        bObj.order_id = order_id
                        bObj.plan_id = data['plan_id']
                        if valObjline.data['beizhu']:
                            bObj.beizhu = valObjline.data['beizhu']
                        bObj.notes_id = valObjline.data['notes_id']
                        if valObjline.data['people'] :
                            bObj.people = valObjline.data['people']
                            bObj.people_department = valObjline.data['people_department']
                            bObj.people_post = valObjline.data['people_post']
                        if valObjline.data['liuyan']:
                            bObj.liuyan = valObjline.data['liuyan']
                        if valObjline.data['is_sure']:
                            bObj.is_sure = valObjline.data['is_sure']
                        if valObjline.data['status']:
                            bObj.status = valObjline.data['status']
                        #1：计划发货日；2：计划上手日期；3：送检日；4：提货日；5、进仓日期
                        if valObjline.data['warm_mode_id']:
                            bWarm = BaseWarm.objects.get(id=valObjline.data['warm_mode_id'])
                            bObj.warm_mode_id = valObjline.data['warm_mode_id']
                            bObj.warm_day_num = bWarm.warm_time_num
                            if order_id:
                                try:
                                    orderObj = PlanOrder.objects.get(id=data['order_id'],delete_time=None)
                                    orderLine = PlanOrderLine.objects.filter(order_id=data['order_id'],delete_time=None)
                                    time1 = orderLine[0].send_time
                                    time2 = orderObj.plan_time
                                    time3 = orderLine[0].inspect_time
                                    time4 = orderLine[0].delivery_time
                                    time5 = orderLine[0].warehouse_time
                                    for onetime in orderLine:
                                        if time1 < onetime.send_time:
                                            time1 = onetime.send_time
                                        if time3 < onetime.inspect_time:
                                            time3 = onetime.inspect_time
                                        if time4 < onetime.delivery_time:
                                            time4 = onetime.delivery_time
                                        if time5 < onetime.warehouse_time:
                                            time5 = onetime.warehouse_time
                                    if bWarm.warm_type == 1:
                                        bObj.warm_time = time1
                                    elif bWarm.warm_type == 2:
                                        bObj.warm_time = time2
                                    elif bWarm.warm_type == 3:
                                        bObj.warm_time = time3
                                    elif bWarm.warm_type == 4:
                                        bObj.warm_time = time4
                                    elif bWarm.warm_type == 5:
                                        bObj.warm_time = time5
                                except:
                                    pass
                        bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)

            msg = "创建/编辑注意事项成功"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 注意事项
    @csrf_exempt
    def delete(self, request):
        sn = "2040102,2040202,1010210,30101,30201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                try:
                    bObj = OrderNotes.objects.get(notes_id=nid)
                    bObj.delete()
                except:
                    pass
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "注意事项删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "注意事项不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取订单 注意事项所有
    @csrf_exempt
    def get(self, request):
        sn = "2040102,2040202,1010210,30101,30201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderNotesOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                searchData = []
                lclothClass = ClothClass.objects.filter(delete_time=None)
                for l0 in lclothClass:
                    samp = {}
                    lcloth = Cloth.objects.filter(delete_time=None, class_id=l0.id)
                    list2 = []
                    for l1 in lcloth:
                        tamp = {}
                        lcat = ClothCategory.objects.filter(delete_time=None, cloth_id=l1.id)
                        list3 = []
                        for l2 in lcat:
                            zamp = {}
                            zamp['category_id'] = l2.id
                            zamp['category_name'] = l2.category_name
                            list3.append(zamp)
                        tamp['cloth_id'] = l1.id
                        tamp['cloth'] = l1.cloth
                        tamp['zub'] = list3
                        list2.append(tamp)
                    samp['cloth_class_id'] = l0.id
                    samp['cloth_class_name'] = l0.cloth_class_name
                    samp['sub'] = list2
                    searchData.append(samp)
                # 检索参数
                cloth_class_id = valObj.data['cloth_class_id'] if valObj.data['cloth_class_id'] else 0
                cloth_id = valObj.data['cloth_id'] if valObj.data['cloth_id'] else 0
                category_id = valObj.data['category_id'] if valObj.data['category_id'] else 0
                is_sure = valObj.data['is_sure'] if valObj.data['is_sure'] else 0
                # 查询数据
                notesAll = ClothNotes.objects.filter(delete_time=None).order_by('category_id', 'weight')
                if category_id:
                    notesAll = notesAll.filter(category_id = category_id)

                else:
                    if cloth_id:
                        clothCatObj = ClothCategory.objects.filter(cloth_id = cloth_id)
                        cat_id_lst =  [one.id for one in clothCatObj]
                        notesAll = notesAll.filter(category_id__in=cat_id_lst)
                    else:
                        if cloth_class_id:
                            clothObj = Cloth.objects.filter(class_id=cloth_class_id)
                            cloth_id_list = [one.id for one in clothObj]
                            clothCatObj = ClothCategory.objects.filter(cloth_id__in=cloth_id_list)
                            cat_id_lst = [one.id for one in clothCatObj]
                            notesAll = notesAll.filter(category_id__in=cat_id_lst)

                noteslist = notesAll.values()
                notes_all_num = 0
                notes_sure_num = 0
                notes_nosure_num = 0
                for one in noteslist:
                    noteCat = ClothCategory.objects.get(delete_time=None, id=one["category_id"])
                    noteCloth = Cloth.objects.get(id=noteCat.cloth_id, delete_time=None)
                    noteClothClass = ClothClass.objects.get(id=noteCloth.class_id)
                    one["cloth_class_name"] = noteClothClass.cloth_class_name
                    one["cloth_class_id"] = noteClothClass.id
                    one["category_name"] = noteCat.category_name
                    one["category_id"] = noteCat.id
                    one["cloth_name"] = noteCloth.cloth
                    one["cloth_id"] = noteCloth.id
                    one['notes_id'] = one['id']
                    orderNote = OrderNotes.objects.filter(notes_id=one["id"], plan_id=valObj.data['plan_id'])
                    if orderNote.count() > 0:
                        notes_all_num = notes_all_num+1
                        if orderNote[0].is_sure==1:
                            notes_sure_num = notes_sure_num+1
                        else:
                            notes_nosure_num = notes_nosure_num+1
                        one['id'] = orderNote[0].id
                        one['people'] = orderNote[0].people
                        one['people_department'] = orderNote[0].people_department
                        one['people_post'] = orderNote[0].people_post
                        one['liuyan'] = orderNote[0].liuyan
                        one['beizhu'] = orderNote[0].beizhu
                        one['warm_time'] = orderNote[0].warm_time
                        one['warm_day_num'] = orderNote[0].warm_day_num
                        one['warm_mode_id'] = orderNote[0].warm_mode_id
                        try:
                            baseWarm = BaseWarm.objects.get(id=orderNote[0].warm_mode_id)
                            one["warm_num_name"] = baseWarm.warm_num_name
                        except:
                            one["warm_num_name"] =None
                        dt1 = datetime.now()
                        dt2 = orderNote[0].warm_time
                        one["down_days_num"] = downDay(dt1, dt2)
                        one['is_active'] = 1
                    else:
                        one['is_active'] = 0
                        one['id'] = None
                temp = {}
                temp["data"] = noteslist
                temp['notes_nosure_num'] = notes_nosure_num
                temp['notes_sure_num'] = notes_sure_num
                temp['notes_all_num'] = notes_all_num
                temp['searchData'] = searchData
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的注意事项信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class orderNotesOneView(APIView):
    # 获取订单 注意事项（当前面辅料）
    @csrf_exempt
    def get(self, request, nid):
        sn = "2040102,2040202,1010210,30101,30201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderNotesOne1Serializer(data=request.query_params)
        if valObj.is_valid():
            try:
                searchData = []
                lclothClass = ClothClass.objects.filter(delete_time=None)
                for l0 in lclothClass:
                    samp = {}
                    lcloth = Cloth.objects.filter(delete_time=None,class_id=l0.id)
                    list2 = []
                    for l1 in lcloth:
                        tamp = {}
                        lcat = ClothCategory.objects.filter(delete_time=None,cloth_id=l1.id)
                        list3 = []
                        for l2 in lcat:
                            zamp={}
                            zamp['category_id'] = l2.id
                            zamp['category_name'] = l2.category_name
                            list3.append(zamp)
                        tamp['cloth_id'] = l1.id
                        tamp['cloth'] = l1.cloth
                        tamp['zub'] = list3
                        list2.append(tamp)
                    samp['cloth_class_id'] = l0.id
                    samp['cloth_class_name'] = l0.cloth_class_name
                    samp['sub'] = list2
                    searchData.append(samp)

                # 检索参数
                cloth_class_id = valObj.data['cloth_class_id'] if valObj.data['cloth_class_id']  else 0
                cloth_id = valObj.data['cloth_id'] if valObj.data['cloth_id']  else 0
                category_id = valObj.data['category_id'] if valObj.data['category_id']  else 0
                is_sure = valObj.data['is_sure'] if valObj.data['is_sure'] is not None else 2
                #统计数据
                notes_all_num = 0
                notes_sure_num = 0
                notes_nosure_num = 0
                # 订单注意事项
                orderNote = OrderNotes.objects.filter(delete_time=None,plan_id=nid)


                # 检索
                if is_sure !=2:
                    orderNote = orderNote.filter(is_sure=is_sure)
                note_id_list = [one.notes_id for one in orderNote]
                notesAll = ClothNotes.objects.filter(delete_time=None, id__in=note_id_list).order_by('category_id',
                                                                                                     'weight')
                if category_id:
                    notesAll = notesAll.filter(category_id = category_id)

                else:
                    if cloth_id:
                        clothCatObj = ClothCategory.objects.filter(cloth_id = cloth_id)
                        cat_id_lst =  [one.id for one in clothCatObj]
                        notesAll = notesAll.filter(category_id__in=cat_id_lst)
                    else:
                        if cloth_class_id:
                            clothObj = Cloth.objects.filter(class_id=cloth_class_id)
                            cloth_id_list = [one.id for one in clothObj]
                            clothCatObj = ClothCategory.objects.filter(cloth_id__in=cloth_id_list)
                            cat_id_lst = [one.id for one in clothCatObj]
                            notesAll = notesAll.filter(category_id__in=cat_id_lst)

                noteslist  = notesAll.values()
                for one in noteslist:
                    noteCat = ClothCategory.objects.get(delete_time=None, id=one["category_id"])
                    noteCloth = Cloth.objects.get(id=noteCat.cloth_id, delete_time=None)
                    noteClothClass = ClothClass.objects.get(id=noteCloth.class_id)
                    one["cloth_class_name"] = noteClothClass.cloth_class_name
                    one["cloth_class_id"] = noteClothClass.id
                    one["category_name"] = noteCat.category_name
                    one["category_id"] = noteCat.id
                    one["cloth_name"] = noteCloth.cloth
                    one["cloth_id"] = noteCloth.id
                    one['notes_id'] = one['id']
                    orderNote =OrderNotes.objects.filter(plan_id=nid,notes_id=one['id'])
                    if orderNote.count()>0:
                        notes_all_num = notes_all_num + 1
                        if orderNote[0].is_sure == 1:
                            notes_sure_num = notes_sure_num + 1
                        else:
                            notes_nosure_num = notes_nosure_num + 1
                        one['id'] = orderNote[0].id
                        one['people'] = orderNote[0].people
                        one['people_department'] = orderNote[0].people_department
                        one['people_post'] = orderNote[0].people_post
                        one['liuyan'] = orderNote[0].liuyan
                        one['beizhu'] = orderNote[0].beizhu
                        one['warm_time'] = orderNote[0].warm_time
                        one['warm_day_num'] = orderNote[0].warm_day_num
                        one['warm_mode_id'] = orderNote[0].warm_mode_id
                        try:
                            baseWarm = BaseWarm.objects.get(id=orderNote[0].warm_mode_id)
                            one["warm_num_name"] = baseWarm.warm_num_name
                        except:
                            one["warm_num_name"] = None
                        dt1 = datetime.now()
                        dt2 = orderNote[0].warm_time
                        one["down_days_num"] = downDay(dt1,dt2)
                        one['is_active'] = 1
                        one['is_sure'] = orderNote[0].is_sure
                    else:
                        one['is_active'] = 0
                        one['id'] = None
                # 检索元数据
                temp = {}
                temp["data"] =noteslist
                temp['notes_nosure_num'] = notes_nosure_num
                temp['notes_sure_num'] = notes_sure_num
                temp['notes_all_num'] = notes_all_num
                temp['searchData'] = searchData
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的注意事项信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

# 日期之差
def downDay(d1,d2):
    if d1 and d2:
        dayNum = (d2.date()-d1.date()).days
    else:
        dayNum = None
    return dayNum


############################订单管理-其他注意事项###############################################

class orderNotesOtherView(APIView):
    # 添加/编辑 注意事项
    @csrf_exempt
    def post(self, request):
        sn = "2040102,2040202,1010210"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = orderNotesSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            order_id = valObj.data['order_id'] if valObj.data['order_id'] is not None else 0
            dataone = data['data']
            dt = datetime.now()
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderNotesLineSerializer(data=done)
                if not valObjline.is_valid():
                    msg = valObjline.errors
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
                if valObjline.is_valid():
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderNotesOther.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                if valObjline.data['notes_id']:
                                    bList = OrderNotesOther.objects.filter(plan_id=valObj.data['plan_id'],notes_id=valObjline.data['notes_id'])
                                    if bList.count()>0:
                                        bObj = bList[0]
                                        bObj.update_time = dt
                                    else:
                                        bObj = OrderNotesOther()
                                        bObj.create_time = dt
                        except:
                            bObj = OrderNotesOther()
                            bObj.create_time = dt
                        bObj.order_id = order_id
                        bObj.plan_id = data['plan_id']
                        if valObjline.data['beizhu']:
                            bObj.beizhu = valObjline.data['beizhu']
                        bObj.notes_id = valObjline.data['notes_id']
                        if valObjline.data['people'] :
                            bObj.people = valObjline.data['people']
                            bObj.people_department = valObjline.data['people_department']
                            bObj.people_post = valObjline.data['people_post']
                        if valObjline.data['liuyan']:
                            bObj.liuyan = valObjline.data['liuyan']
                        if valObjline.data['is_sure']:
                            bObj.is_sure = valObjline.data['is_sure']
                        if valObjline.data['status']:
                            bObj.status = valObjline.data['status']
                        #1：计划发货日；2：计划上手日期；3：送检日；4：提货日；5、进仓日期
                        if valObjline.data['warm_mode_id']:
                            bWarm = BaseWarm.objects.get(id=valObjline.data['warm_mode_id'])
                            bObj.warm_mode_id = valObjline.data['warm_mode_id']
                            bObj.warm_day_num = bWarm.warm_time_num
                            if order_id:
                                try:
                                    orderObj = PlanOrder.objects.get(id=data['order_id'],delete_time=None)
                                    orderLine = PlanOrderLine.objects.filter(order_id=data['order_id'],delete_time=None)
                                    time1 = orderLine[0].send_time
                                    time2 = orderObj.plan_time
                                    time3 = orderLine[0].inspect_time
                                    time4 = orderLine[0].delivery_time
                                    time5 = orderLine[0].warehouse_time
                                    for onetime in orderLine:
                                        if time1 < onetime.send_time:
                                            time1 = onetime.send_time
                                        if time3 < onetime.inspect_time:
                                            time3 = onetime.inspect_time
                                        if time4 < onetime.delivery_time:
                                            time4 = onetime.delivery_time
                                        if time5 < onetime.warehouse_time:
                                            time5 = onetime.warehouse_time
                                    if bWarm.warm_type == 1:
                                        bObj.warm_time = time1
                                    elif bWarm.warm_type == 2:
                                        bObj.warm_time = time2
                                    elif bWarm.warm_type == 3:
                                        bObj.warm_time = time3
                                    elif bWarm.warm_type == 4:
                                        bObj.warm_time = time4
                                    elif bWarm.warm_type == 5:
                                        bObj.warm_time = time5
                                except:
                                    pass
                        bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)

            msg = "创建/编辑注意事项成功"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 注意事项
    @csrf_exempt
    def delete(self, request):
        sn = "2040102,2040202,1010210"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                try:
                    bObj = OrderNotesOther.objects.get(notes_id=nid)
                    bObj.delete()
                except:
                    pass
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "注意事项不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取订单 注意事项所有
    @csrf_exempt
    def get(self, request):
        sn = "2040102,2040202,1010210"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderNotesOtherSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                searchData = []
                lclothClass = OtherCategory.objects.filter(delete_time=None)
                for l0 in lclothClass:
                    samp = {}
                    lcloth = OtherSubCategory.objects.filter(delete_time=None, category_id=l0.id)
                    list2 = []
                    for l1 in lcloth:
                        tamp = {}
                        lcat = OtherCategorySetting.objects.filter(delete_time=None, sub_category_id=l1.id)
                        list3 = []
                        for l2 in lcat:
                            zamp = {}
                            zamp['other_category_setting_id'] = l2.id
                            zamp['category_set_name'] = l2.category_set_name
                            list3.append(zamp)
                        tamp['other_sub_category_id'] = l1.id
                        tamp['sub_name'] = l1.sub_name
                        tamp['zub'] = list3
                        list2.append(tamp)
                    samp['other_category_id'] = l0.id
                    samp['category_name'] = l0.category_name
                    samp['sub'] = list2
                    searchData.append(samp)
                # 检索
                other_category_id = valObj.data['other_category_id'] if valObj.data['other_category_id'] else 0
                other_sub_category_id = valObj.data['other_sub_category_id'] if valObj.data['other_sub_category_id'] else 0
                other_category_setting_id = valObj.data['other_category_setting_id'] if valObj.data['other_category_setting_id'] else 0

                notesAll = OtherNotes.objects.filter(delete_time=None).order_by('category_setting_id', 'weight')
                if other_category_setting_id:
                    notesAll = notesAll.filter(category_setting_id = other_category_setting_id)

                else:
                    if other_sub_category_id:
                        clothCatObj = OtherCategorySetting.objects.filter(sub_category_id = other_sub_category_id)
                        cat_id_lst =  [one.id for one in clothCatObj]
                        notesAll = notesAll.filter(category_setting_id__in=cat_id_lst)
                    else:
                        if other_category_id:
                            clothObj = OtherSubCategory.objects.filter(category_id=other_category_id)
                            cloth_id_list = [one.id for one in clothObj]
                            clothCatObj = ClothCategory.objects.filter(sub_category_id__in=cloth_id_list)
                            cat_id_lst = [one.id for one in clothCatObj]
                            notesAll = notesAll.filter(category_setting_id__in=cat_id_lst)
                noteslist = notesAll.values()
                notes_all_num = 0
                notes_sure_num = 0
                notes_nosure_num = 0
                for one in noteslist:
                    noteCat = OtherCategorySetting.objects.get(delete_time=None, id=one["category_setting_id"])
                    noteCloth = OtherSubCategory.objects.get(id=noteCat.sub_category_id, delete_time=None)
                    noteClothClass = OtherCategory.objects.get(id=noteCloth.category_id)
                    one["cloth_class_name"] = noteClothClass.category_name
                    one["cloth_class_id"] = noteClothClass.id
                    one["category_name"] = noteCat.category_set_name
                    one["category_id"] = noteCat.id
                    one["cloth_name"] = noteCloth.sub_name
                    one["cloth_id"] = noteCloth.id
                    one['notes_id'] = one['id']
                    orderNote = OrderNotesOther.objects.filter(notes_id=one["id"], plan_id=valObj.data['plan_id'])
                    if orderNote.count() > 0:
                        notes_all_num = notes_all_num+1
                        if orderNote[0].is_sure==1:
                            notes_sure_num = notes_sure_num+1
                        else:
                            notes_nosure_num = notes_nosure_num+1
                        one['id'] = orderNote[0].id
                        one['people'] = orderNote[0].people
                        one['people_department'] = orderNote[0].people_department
                        one['people_post'] = orderNote[0].people_post
                        one['liuyan'] = orderNote[0].liuyan
                        one['beizhu'] = orderNote[0].beizhu
                        one['warm_time'] = orderNote[0].warm_time
                        one['warm_day_num'] = orderNote[0].warm_day_num
                        one['warm_mode_id'] = orderNote[0].warm_mode_id
                        try:
                            baseWarm = BaseWarm.objects.get(id=orderNote[0].warm_mode_id)
                            one["warm_num_name"] = baseWarm.warm_num_name
                        except:
                            one["warm_num_name"] =None
                        dt1 = datetime.now()
                        dt2 = orderNote[0].warm_time
                        one["down_days_num"] = downDay(dt1, dt2)
                        one['is_active'] = 1
                    else:
                        one['is_active'] = 0
                        one['id'] = None
                temp = {}
                temp["data"] = noteslist
                temp['notes_nosure_num'] = notes_nosure_num
                temp['notes_sure_num'] = notes_sure_num
                temp['notes_all_num'] = notes_all_num
                temp['searchData'] = searchData
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的注意事项信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class orderNotesOtherOneView(APIView):
    # 获取订单 注意事项（当前面辅料）
    @csrf_exempt
    def get(self, request, nid):
        sn = "2040102,2040202,1010210"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderNotesOtherSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                searchData = []
                lclothClass = OtherCategory.objects.filter(delete_time=None)
                for l0 in lclothClass:
                    samp = {}
                    lcloth = OtherSubCategory.objects.filter(delete_time=None, category_id=l0.id)
                    list2 = []
                    for l1 in lcloth:
                        tamp = {}
                        lcat = OtherCategorySetting.objects.filter(delete_time=None, sub_category_id=l1.id)
                        list3 = []
                        for l2 in lcat:
                            zamp = {}
                            zamp['other_category_setting_id'] = l2.id
                            zamp['category_set_name'] = l2.category_set_name
                            list3.append(zamp)
                        tamp['other_sub_category_id'] = l1.id
                        tamp['sub_name'] = l1.sub_name
                        tamp['zub'] = list3
                        list2.append(tamp)
                    samp['other_category_id'] = l0.id
                    samp['category_name'] = l0.category_name
                    samp['sub'] = list2
                    searchData.append(samp)
                # 检索
                other_category_id = valObj.data['other_category_id'] if valObj.data['other_category_id'] else 0
                other_sub_category_id = valObj.data['other_sub_category_id'] if valObj.data[
                    'other_sub_category_id'] else 0
                other_category_setting_id = valObj.data['other_category_setting_id'] if valObj.data[
                    'other_category_setting_id'] else 0
                is_sure = valObj.data['is_sure'] if valObj.data['is_sure'] is not None else 2
                notes_all_num = 0
                notes_sure_num = 0
                notes_nosure_num = 0
                orderNote = OrderNotesOther.objects.filter(plan_id=nid)
                if is_sure !=2:
                    orderNote = orderNote.filter(is_sure=is_sure)
                note_id_list = [one.notes_id for one in orderNote]
                notesAll = OtherNotes.objects.filter(delete_time=None, id__in=note_id_list).order_by('category_setting_id','weight')
                if other_category_setting_id:
                    notesAll = notesAll.filter(category_setting_id = other_category_setting_id)

                else:
                    if other_sub_category_id:
                        clothCatObj = OtherCategorySetting.objects.filter(sub_category_id = other_sub_category_id)
                        cat_id_lst =  [one.id for one in clothCatObj]
                        notesAll = notesAll.filter(category_setting_id__in=cat_id_lst)
                    else:
                        if other_category_id:
                            clothObj = OtherSubCategory.objects.filter(category_id=other_category_id)
                            cloth_id_list = [one.id for one in clothObj]
                            clothCatObj = ClothCategory.objects.filter(sub_category_id__in=cloth_id_list)
                            cat_id_lst = [one.id for one in clothCatObj]
                            notesAll = notesAll.filter(category_setting_id__in=cat_id_lst)
                noteslist  = notesAll.values()
                # other_category其他面辅料类别，other_sub_category,其他注意事项名称，other_cat_setting其他注意事项类别,other_notes,其他注意事项
                for one in noteslist:
                    noteCat = OtherCategorySetting.objects.get(delete_time=None, id=one["category_setting_id"])
                    noteCloth = OtherSubCategory.objects.get(id=noteCat.sub_category_id, delete_time=None)
                    noteClothClass = OtherCategory.objects.get(id=noteCloth.category_id)
                    one["cloth_class_name"] = noteClothClass.category_name
                    one["cloth_class_id"] = noteClothClass.id
                    one["category_name"] = noteCat.category_set_name
                    one["category_id"] = noteCat.id
                    one["cloth_name"] = noteCloth.sub_name
                    one["cloth_id"] = noteCloth.id
                    one['notes_id'] = one['id']
                    orderNote =OrderNotesOther.objects.filter(plan_id=nid,notes_id=one['id'])
                    if orderNote.count()>0:
                        notes_all_num = notes_all_num + 1
                        if orderNote[0].is_sure == 1:
                            notes_sure_num = notes_sure_num + 1
                        else:
                            notes_nosure_num = notes_nosure_num + 1
                        one['id'] = orderNote[0].id
                        one['people'] = orderNote[0].people
                        one['people_department'] = orderNote[0].people_department
                        one['people_post'] = orderNote[0].people_post
                        one['liuyan'] = orderNote[0].liuyan
                        one['beizhu'] = orderNote[0].beizhu
                        one['warm_time'] = orderNote[0].warm_time
                        one['warm_day_num'] = orderNote[0].warm_day_num
                        one['warm_mode_id'] = orderNote[0].warm_mode_id
                        try:
                            baseWarm = BaseWarm.objects.get(id=orderNote[0].warm_mode_id)
                            one["warm_num_name"] = baseWarm.warm_num_name
                        except:
                            one["warm_num_name"] = None
                        dt1 = datetime.now()
                        dt2 = orderNote[0].warm_time
                        one["down_days_num"] = downDay(dt1,dt2)
                        one['is_active'] = 1
                        one['is_sure'] = orderNote[0].is_sure
                    else:
                        one['is_active'] = 0
                        one['id'] = None
                temp = {}
                temp["data"] =noteslist
                temp['notes_nosure_num'] = notes_nosure_num
                temp['notes_sure_num'] = notes_sure_num
                temp['notes_all_num'] = notes_all_num
                temp['searchData'] = searchData
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的注意事项信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-发货方案###############################################

class shipmentView(APIView):
    # 添加/编辑 发货方案
    @csrf_exempt
    def post(self, request):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = orderClothShipSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderClothLineShipSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
                subdata = done['sub_data']
                s_flag = 0
                s_num = 0
                for sdone in subdata:
                    s_num = s_num + 1
                    valObjline = orderClothLineSubShipSerializer(data=sdone)
                    if not valObjline.is_valid():
                        s_flag = 1
                        samp = {}
                        samp['msg'] = valObjline.errors
                        samp['key_num'] = s_num
                        l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0 and s_flag == 0:
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderClothShip.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = OrderClothShip()
                                bObj.create_time = dt
                        except:
                            bObj = OrderClothShip()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        # bObj.plan_id = data['plan_id']
                        bObj.cloth_type = done['cloth_type']
                        bObj.cloth_cat = done['cloth_cat']
                        bObj.cloth_name = done['cloth_name']
                        bObj.supplier = done['supplier']
                        # bObj.buy_all_num = done['buy_all_num']
                        bObj.all_amount = done['all_amount']
                        bObj.order_cloth_id = data['order_cloth_id']
                        bObj.save()
                        if mid:
                            order_cloth_ship_id = mid
                        else:
                            ocOne = OrderClothShip.objects.latest("id")
                            order_cloth_ship_id = ocOne.id
                        # 保存面辅料的sku
                        subdata = done['sub_data']
                        for sub in subdata:
                            try:
                                s_id = sub["id"]
                                if s_id:
                                    sbObj = OrderClothLineShip.objects.get(id=s_id)
                                    sbObj.update_time = dt
                                else:
                                    sbObj = OrderClothLineShip()
                                    sbObj.create_time = dt
                            except:
                                sbObj = OrderClothLineShip()
                                sbObj.create_time = dt
                            sbObj.order_id = data['order_id']
                            sbObj.order_cloth_id = data['order_cloth_id']
                            if done['cloth_type'] ==4:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                                sbObj.specs = sub['specs']
                            if done['cloth_type'] ==3:
                                sbObj.specs = sub['specs']
                            if done['cloth_type'] ==2:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                            sbObj.guige = sub['guige']
                            sbObj.buy_num = sub['buy_num']
                            sbObj.price = sub['price']
                            sbObj.amount = sub['amount']
                            sbObj.delivery_type = sub['delivery_type']
                            sbObj.delivery_name = sub['delivery_name']
                            sbObj.provide_num = sub['provide_num']
                            sbObj.provide_time = sub['provide_time']
                            sbObj.order_cloth_ship_id = order_cloth_ship_id
                            sbObj.save()

                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "创建/编辑面辅料采购"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 发货方案
    @csrf_exempt
    def delete(self, request):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = OrderClothShip.objects.get(id=nid)
                dt = datetime.now()
                subObj = OrderClothLineShip.objects.filter(order_cloth_id=bObj.id)
                for one in subObj:
                    one.delete_time = dt
                    one.save()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "发货方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class shipmentOneView(APIView):
    # 获取订单 面辅料采购入库
    @csrf_exempt
    def get(self, request, nid):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderCloth = OrderCloth.objects.get(id=nid)
                orderObj = PlanOrder.objects.get(delete_time=None, id=orderCloth.order_id)
                orderClothShip = OrderClothShip.objects.filter(delete_time=None,order_cloth_id=nid)
                samplist=[]
                for one in orderClothShip:
                    samp={}
                    samp['cloth_type'] = one.cloth_type
                    samp['cloth_cat'] = one.cloth_cat
                    samp['cloth_name'] = one.cloth_name
                    # samp['delivery_type'] = one.delivery_type
                    # samp['delivery_name'] = one.delivery_name
                    samp['is_inspect'] = one.is_inspect
                    samp['buy_all_num'] = one.buy_all_num
                    samp['loss_lv'] = one.loss_lv
                    samp['supplier'] = one.supplier
                    samp['all_amount'] = one.all_amount
                    samp['order_cloth_ship_id'] = one.id
                    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=nid,order_cloth_ship_id=one.id).order_by('color', 'specs')
                    rObjList = rObj.values()
                    for one1 in rObjList:
                        one1["order_cloth_ship_line_id"] = one1["id"]
                        del one1["id"]
                    samp['sub_data'] = rObjList
                    samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                temp["orderObj"] = model_to_dict(orderObj)
                temp['plan_material_id'] = orderCloth.plan_material_id
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的发货方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 面辅料采购入库
    @csrf_exempt
    def put(self, request, nid):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            orderClothlineShip = OrderClothLineShip.objects.get(id=nid)
            orderClothlineShip.is_sure_in_store = 1
            orderClothlineShip.save()
            orderClothShip = OrderClothShip.objects.get(id=orderClothlineShip.order_cloth_ship_id)
            clothShipObj = OrderClothLineShip.objects.filter(order_cloth_ship_id=orderClothlineShip.order_cloth_ship_id)
            flag0 = 1
            for one in clothShipObj:
                if one.is_sure_in_store !=1:
                    flag0 = 0
                    break
            if flag0==1:
                orderClothShip.is_sure_in_store = 1
                orderClothShip.save()
            #
            orderCloth = OrderCloth.objects.get(id=orderClothlineShip.order_cloth_id)
            orderClothShipObj = OrderClothShip.objects.filter(order_cloth_id=orderClothlineShip.order_cloth_id)
            flag1 = 1
            for one in orderClothShipObj:
                if one.is_sure_in_store != 1:
                    flag1 = 0
                    break
            if flag1 == 1:
                orderCloth.is_sure_in_store = 1
                orderCloth.save()
            temp = {}
            temp['error_code'] = 0
            temp['message'] = "确认收发货全部完成"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的面辅料采购项"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-业务组织管理###############################################

class managementView(APIView):
    # 添加/编辑 面辅料采购
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = orderClothSerializer(data=request.data)
        if valObj.is_valid():
            work_type = valObj.data['work_type'] if valObj.data['work_type'] is not None else ""
            dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderClothLineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
                subdata = done['sub_data']
                s_flag = 0
                s_num = 0
                for sdone in subdata:
                    s_num = s_num + 1
                    valObjline = orderClothLineSubSerializer(data=sdone)
                    if not valObjline.is_valid():
                        s_flag = 1
                        samp = {}
                        samp['msg'] = valObjline.errors
                        samp['key_num'] = s_num
                        l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0 and s_flag == 0:
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderCloth.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = OrderCloth()
                                bObj.create_time = dt
                        except:
                            bObj = OrderCloth()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        bObj.plan_id = data['plan_id']
                        bObj.cloth_type = done['cloth_type']
                        bObj.cloth_cat = done['cloth_cat']
                        bObj.cloth_name = done['cloth_name']
                        bObj.delivery_type = done['delivery_type']
                        bObj.delivery_name = done['delivery_name']
                        bObj.is_inspect = done['is_inspect']
                        bObj.buy_all_num = done['buy_all_num']
                        bObj.loss_lv = done['loss_lv']
                        bObj.save()
                        if mid:
                            order_cloth_id = mid
                        else:
                            ocOne = OrderCloth.objects.latest("id")
                            order_cloth_id = ocOne.id
                        subdata = done['sub_data']
                        for sub in subdata:
                            try:
                                s_id = sub["id"]
                                if mid:
                                    sbObj = OrderClothLine.objects.get(id=s_id)
                                    sbObj.update_time = dt
                                else:
                                    sbObj = OrderClothLine()
                                    sbObj.create_time = dt
                            except:
                                sbObj = OrderClothLine()
                                sbObj.create_time = dt
                            sbObj.order_id = data['order_id']
                            sbObj.order_cloth_id = order_cloth_id
                            if done['cloth_type'] ==4:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                                sbObj.specs = sub['specs']
                            if done['cloth_type'] ==3:
                                sbObj.specs = sub['specs']
                            if done['cloth_type'] ==2:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                            sbObj.guige = sub['guige']
                            sbObj.buy_num = sub['buy_num']
                            sbObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.is_buyprogram =1
                    bg_num = OrderCloth.objects.filter(order_id=data['order_id'],delete_time=None).count()
                    order.buyprogram_num =bg_num
                    if dhkhao:
                        order.dhkhao = dhkhao
                    if work_type:
                        order.work_type = work_type
                    order.save()
                except:
                    pass
                msg = "创建/编辑面辅料采购"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 面辅料采购
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = OrderCloth.objects.get(id=nid)
                dt = datetime.now()
                subObj = OrderClothLine.objects.filter(order_cloth_id=bObj.id)
                for one in subObj:
                    one.delete_time = dt
                    one.save()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "出货方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class managementOneView(APIView):
    # 获取订单 面辅料采购
    @csrf_exempt
    def get(self, request, nid):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
                orderCloth = OrderCloth.objects.filter(order_id=nid)
                samplist=[]
                for one in orderCloth:
                    samp={}
                    samp['cloth_type'] = one.cloth_type
                    samp['cloth_cat'] = one.cloth_cat
                    samp['cloth_name'] = one.cloth_name
                    samp['delivery_type'] = one.delivery_type
                    samp['delivery_name'] = one.delivery_name
                    samp['is_inspect'] = one.is_inspect
                    samp['buy_all_num'] = one.buy_all_num
                    samp['loss_lv'] = one.loss_lv
                    samp['id'] = one.id
                    rObj = OrderClothLine.objects.filter(delete_time=None, order_cloth_id=one.id).order_by('color', 'specs')
                    samp['sub_data'] = rObj.values()
                    samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                temp["orderObj"] = model_to_dict(orderObj)
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的面辅料采购信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-装箱录入要求###############################################

class packingView(APIView):
    # 添加/编辑 装箱要求
    @csrf_exempt
    def post(self, request):
        sn = "20301,301,302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = packingSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = packingLineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderLinePacking.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                cobj = OrderLinePacking.objects.filter(order_line_id=done['order_line_id'],delete_time=None)
                                if cobj.count()>0:
                                    bObj = cobj[0]
                                else:
                                    bObj = OrderLinePacking()
                                bObj.create_time = dt
                                bObj.status = 0
                        except:
                            bObj = OrderLinePacking()
                            bObj.create_time = dt
                            bObj.status = 0
                        bObj.order_id = data['order_id']
                        # bObj.plan_id = data['plan_id']
                        bObj.order_custom = done['order_custom']
                        bObj.contract_num = done['contract_num']
                        bObj.order_type = done['order_type']
                        bObj.comments = done['comments']
                        bObj.brand = done['brand']
                        bObj.specs = done['specs']
                        bObj.order_line_id = done['order_line_id']
                        bObj.scale = done['scale']
                        bObj.cuttle = done['cuttle']
                        # bObj.plan_id = data['plan_id']
                        bObj.save()

                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "创建/编辑 装箱要求"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 发货方案
    @csrf_exempt
    def delete(self, request):
        sn = "20301,301,302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = OrderClothShip.objects.get(id=nid)
                dt = datetime.now()
                subObj = OrderClothLineShip.objects.filter(order_cloth_id=bObj.id)
                for one in subObj:
                    one.delete_time = dt
                    one.save()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "发货方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class packingOneView(APIView):
    # 获取订单 装箱要求
    @csrf_exempt
    def get(self, request, nid):
        sn = "20301,301,302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
                orderLine = PlanOrderLine.objects.filter(order_id=nid)
                samplist=[]
                dis_list = []
                for one in orderLine:
                    # 获取出货方案
                    outObj = OutStock.objects.filter(order_line_id=one.id)
                    dis_temp = []
                    for o in outObj:
                        dis_temp_one = []
                        dis_temp_one.append(o.color)
                        dis_temp_one.append(o.specs)
                        dis_temp.append(dis_temp_one)
                    dis_list.append(dis_temp)
                    samp={}
                    o_pack = OrderLinePacking.objects.filter(order_line_id=one.id)
                    if o_pack.count()>0:
                        samp = model_to_dict(o_pack[0])
                        samplist.append(samp)
                    else:
                        samp['order_custom'] = one.order_custom
                        samp['order_type'] = one.order_type
                        samp['contract_num'] = one.contract_num
                        samp['brand'] = orderObj.brand
                        samp['id'] = 0
                        samp['order_line_id'] = one.id
                        samp['order_id'] = nid
                        samp['specs'] = ""
                        samp['scale'] = ""
                        samp['cuttle'] = ""
                        samp['comments'] = ""
                        samplist.append(samp)
                is_pack_all = 0
                for n in range(len(dis_list) - 1):
                    if (dis_list[n] == dis_list[n + 1]):
                        is_pack_all = 1
                    else:
                        is_pack_all = 0
                        break
                    print(n)
                temp = {}
                temp["data"] = samplist
                temp["order_id"] = nid
                temp["is_pack_all"] = is_pack_all
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的装箱要求"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################订单管理-装箱指示###############################################

class packingLineView(APIView):
    # 添加/编辑 装箱指示
    @csrf_exempt
    def post(self, request):
        sn = "20301,301,302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        for one in data:
            valObj = packingSublineSerializer(data=one)
            if valObj.is_valid():
                #################校验数据################################
                d_flag = 0
                d_num = 0
                l_msg = []
                dataone = one['data']
                for done in dataone:
                    d_num = d_num + 1
                    valObjline = packingSubLineoneSerializer(data=done)
                    if not valObjline.is_valid():
                        d_flag = 1
                        samp = {}
                        samp['msg'] = valObjline.errors
                        samp['key_num'] = d_num
                        l_msg.append(samp)
                #################校验数据################################
            dt = datetime.now()
            ##############保存装箱指示#############################
            if d_flag == 0:
                for subOne in data:
                    dataone = subOne['data']
                    for done in dataone:
                        try:
                            try:
                                mid = done["id"]
                                if mid:
                                    bObj = OrderLinePackingSub.objects.get(id=mid)
                                    bObj.update_time = dt
                                else:
                                    cobj = OrderLinePackingSub.objects.filter(out_stock_id=done['out_stock_id'],delete_time=None)
                                    if cobj.count()>0:
                                        bObj = cobj[0]
                                    else:
                                        bObj = OrderLinePackingSub()
                                    bObj.create_time = dt
                                    bObj.status = 0
                            except:
                                cobj = OrderLinePackingSub.objects.filter(out_stock_id=done['out_stock_id'],
                                                                          delete_time=None)
                                if cobj.count() > 0:
                                    bObj = cobj[0]
                                else:
                                    bObj = OrderLinePackingSub()
                                bObj.create_time = dt
                                bObj.status = 0
                            bObj.order_line_id = subOne['order_line_id']
                            bObj.out_stock_id = done['out_stock_id']
                            bObj.parent_id = done['parent_id']
                            bObj.pack_num = done['pack_num']
                            bObj.save()
                            #更改装箱要求的状态
                            try:
                                ppObj = OrderLinePacking.objects.get(order_line_id = subOne['order_line_id'])
                                ppObj.status = 1
                                ppObj.save()
                            except:
                                pass

                        except:
                            msg = "参数错误"
                            error_code = 10030
                            request = request.method + '  ' + request.get_full_path()
                            post_result = {
                                "error_code": error_code,
                                "message": msg,
                                "request": request,
                            }
                            return Response(post_result)
                msg = "创建/编辑 装箱指示"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 发货方案
    @csrf_exempt
    def delete(self, request):
        sn = "20301,301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = OrderClothShip.objects.get(id=nid)
                dt = datetime.now()
                subObj = OrderClothLineShip.objects.filter(order_cloth_id=bObj.id)
                for one in subObj:
                    one.delete_time = dt
                    one.save()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "发货方案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料方案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class packingLineOneView(APIView):
    # 获取订单 装箱要求
    @csrf_exempt
    def get(self, request, nid):
        sn = "20301,301,302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderLine = PlanOrderLine.objects.filter(id=nid)
                outObj = OutStock.objects.filter(order_line_id=nid)
                samplist=[]
                for one in outObj:
                    samp={}
                    o_pack = OrderLinePackingSub.objects.filter(order_line_id=nid,out_stock_id=one.id)
                    if o_pack.count()>0:
                        samp = model_to_dict(o_pack[0])
                    else:
                        samp['parent_id'] = 0
                        samp['id'] = 0
                    samp['order_line_id'] = one.order_line_id
                    samp['color'] = one.color
                    samp['color_name'] = one.color_name
                    samp['color_num'] = one.color_num
                    samp['contract_num'] = one.contract_num
                    samp['specs'] = one.specs
                    samp['out_stock_id'] = one.id
                    samp['order_num'] = one.order_num
                    samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的装箱要求"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-面辅料确认详情###############################################


class shipmentSureView(APIView):
    # 添加/编辑 面辅料确认
    @csrf_exempt
    def post(self, request):
        sn = "20302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = shipmentSureOneSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = shipmentSureSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
                subdata = done['sub_data']
                s_flag = 0
                s_num = 0
                for sdone in subdata:
                    s_num = s_num + 1
                    valObjline = shipmentSureLineShipSerializer(data=sdone)
                    if not valObjline.is_valid():
                        s_flag = 1
                        samp = {}
                        samp['msg'] = valObjline.errors
                        samp['key_num'] = s_num
                        l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存 面辅料确认#############################
            if d_flag == 0 and s_flag == 0:
                for done in dataone:
                    try:
                        try:
                            bObj = OrderClothShip.objects.get(id=done['order_cloth_ship_id'])
                        except:
                            msg = "参数错误"
                            error_code = 10030
                            request = request.method + '  ' + request.get_full_path()
                            post_result = {
                                "error_code": error_code,
                                "message": msg,
                                "request": request,
                            }
                            return Response(post_result)

                        bObj.supplier = done['supplier']
                        bObj.save()
                        # 保存面辅料的sku
                        subdata = done['sub_data']
                        for sub in subdata:
                            try:
                                sbObj = OrderClothLineShip.objects.get(id=sub["order_cloth_ship_line_id"])

                            except:
                                msg = "参数错误"
                                error_code = 10030
                                request = request.method + '  ' + request.get_full_path()
                                post_result = {
                                    "error_code": error_code,
                                    "message": msg,
                                    "request": request,
                                }
                                return Response(post_result)
                            sbObj.sure_comment = sub['sure_comment']
                            sbObj.is_sure = sub['is_sure']
                            sbObj.sample_send_time = sub['sample_send_time']
                            sbObj.save()

                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                # 处理面辅料确认入库状态呢
                sureClothInfo = clothSure(data['order_id'])
                msg = "创建/编辑面辅料采购"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class shipmentSureOneView(APIView):
    # 获取订单 发货方案
    @csrf_exempt
    def get(self, request, nid):
        sn = "20302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = shipmentSureGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderClothOne = OrderClothShip.objects.filter(order_id=nid,delete_time=None)
                cloth_cat_list = []
                cloth_name_list = []
                supplier_list = []
                for n1 in orderClothOne:
                    cloth_cat_list.append(n1.cloth_cat)
                    cloth_name_list.append(n1.cloth_name)
                    supplier_list.append(n1.supplier)
                cloth_cat = valObj.data['cloth_cat'] if valObj.data['cloth_cat'] is not None else ""
                cloth_name = valObj.data['cloth_name'] if valObj.data['cloth_name'] is not None else ""
                supplier = valObj.data['supplier'] if valObj.data['supplier'] is not None else ""
                orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
                orderClothShip = OrderClothShip.objects.filter(delete_time=None,order_id=nid).order_by("order_cloth_id","supplier")
                if cloth_cat:
                    orderClothShip = orderClothShip.filter(cloth_cat = cloth_cat)
                if cloth_name:
                    orderClothShip = orderClothShip.filter(cloth_name=cloth_name)
                if supplier:
                    orderClothShip = orderClothShip.filter(supplier=supplier)
                samplist=[]
                for one in orderClothShip:
                    samp={}
                    samp['cloth_type'] = one.cloth_type
                    samp['cloth_cat'] = one.cloth_cat
                    samp['cloth_name'] = one.cloth_name
                    samp['delivery_type'] = one.delivery_type
                    samp['delivery_name'] = one.delivery_name
                    samp['is_inspect'] = one.is_inspect
                    samp['buy_all_num'] = one.buy_all_num
                    samp['loss_lv'] = one.loss_lv
                    samp['supplier'] = one.supplier
                    samp['order_cloth_ship_id'] = one.id
                    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=one.order_cloth_id,order_cloth_ship_id=one.id).order_by('color', 'specs')
                    sub_data = []
                    for one1 in rObj:
                        zamp = {}
                        zamp["order_cloth_ship_line_id"] = one1.id
                        zamp['color'] = one1.color
                        zamp['color_num'] = one1.color_num
                        zamp['guige'] = one1.guige
                        zamp['specs'] = one1.specs
                        zamp['buy_num'] = one1.buy_num
                        zamp['provide_num'] = one1.provide_num
                        zamp['provide_time'] = one1.provide_time
                        zamp['sample_send_time'] = one1.sample_send_time
                        zamp['sure_comment'] = one1.sure_comment
                        zamp['is_sure'] = one1.is_sure
                        time1 = datetime.now()
                        try:
                            zamp['down_time'] = downDay(time1,one1.provide_time)
                            if zamp['down_time'] <1:
                                zamp['down_time'] = 0
                        except:
                            zamp['down_time'] = 0
                        sub_data.append(zamp)
                    samp['sub_data'] = sub_data
                    # 注意事项
                    notes_all_num, notes_sure_num = getNotesNum(order_id=nid)
                    samp["notes_all_num"] = notes_all_num
                    samp["notes_sure_num"] = notes_sure_num
                    samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                temp["orderObj"] = model_to_dict(orderObj)
                plan_start_date, down_day = getPlanStartdate(nid)
                samp["plan_start_date"] = plan_start_date
                # samp["notes_sure_num"] = notes_sure_num
                # 面辅料缺认
                order_cloth_num, order_cloth_sure_num = getClothSureNum(nid)
                temp["order_cloth_num"] = order_cloth_num
                temp["order_cloth_sure_num"] = order_cloth_sure_num
                temp["order_cloth_no_num"] = order_cloth_num-order_cloth_sure_num
                temp["plan_start_date"] = plan_start_date
                # 洗标吊牌数
                drop_lable_num, drop_lable_sure_num = getDropLableNum(nid)
                temp["drop_lable_num"] = drop_lable_num
                temp["drop_lable_sure_num"] = drop_lable_sure_num
                temp["cloth_cat_list"] = list(set(cloth_cat_list))
                temp["cloth_name_list"] =  list(set(cloth_name_list))
                temp["supplier_list"] = list(set(supplier_list))
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的面辅料采购"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

        # 添加/编辑 面辅料确认

    @csrf_exempt
    def post(self, request, nid):
        sn = "20302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        dataone = data['data']
        l_msg = []
        d_num=0
        d_flag = 0
        for done in dataone:
            d_num = d_num + 1
            valObjline = shipmentSurePostOneSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存 面辅料确认#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    sbObj = OrderClothLineShip.objects.get(id=done["order_cloth_ship_line_id"])

                except:
                    msg = "参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
                sbObj.is_sure = done['is_sure']
                sbObj.save()
            # 处理面辅料确认入库状态呢
            sureClothInfo = clothSure(nid)
            msg = "创建/编辑面辅料采购"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-面辅料确认--洗标吊牌###############################################


class dropView(APIView):
    # 添加/编辑 发货方案
    @csrf_exempt
    def post(self, request):
        sn = "2040104,2040204"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = dropSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = dropOneSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            bObj = OrderClothLine.objects.get(id=done['order_cloth_line_id'])
                        except:
                            msg = "[order_cloth_line_id]参数错误"
                            error_code = 10030
                            request = request.method + '  ' + request.get_full_path()
                            post_result = {
                                "error_code": error_code,
                                "message": msg,
                                "request": request,
                            }
                            return Response(post_result)
                        bObj.create_time = dt
                        bObj.is_inspect = done["is_inspect"]
                        bObj.inspect_content = done["inspect_content"]
                        bObj.drop_status =0
                        bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "创建/编辑洗标吊牌"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class dropOneView(APIView):
    # 获取订单 发货方案
    @csrf_exempt
    def get(self, request, nid):
        sn = "2040104,2040204"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = dropGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderClothOne = OrderCloth.objects.filter(order_id=nid,delete_time=None)
                cloth_cat_list = []
                cloth_name_list = []
                for n1 in orderClothOne:
                    cloth_cat_list.append(n1.cloth_cat)
                    cloth_name_list.append(n1.cloth_name)
                cloth_cat = valObj.data['cloth_cat'] if valObj.data['cloth_cat'] is not None else ""
                cloth_name = valObj.data['cloth_name'] if valObj.data['cloth_name'] is not None else ""
                orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
                fmObj = FactoryMake.objects.filter(order_id=nid)
                str_time = datetime.now()
                plan_start_date_list = []
                for o1 in fmObj:
                    if o1.plan_start_date:
                        plan_start_date_list.append(o1.plan_start_date)
                try:
                    plan_start_date = min(plan_start_date_list)
                    down_day = downDay(plan_start_date,str_time)
                except:
                    plan_start_date = None
                    down_day = None
                orderClothObj = OrderCloth.objects.filter(delete_time=None,order_id=nid).order_by("cloth_cat","cloth_name")
                if cloth_cat:
                    orderClothObj = orderClothObj.filter(cloth_cat = cloth_cat)
                if cloth_name:
                    orderClothObj = orderClothObj.filter(cloth_name = cloth_name)
                samplist=[]
                for one in orderClothObj:
                    orderClothLine = OrderClothLine.objects.filter(delete_time=None,order_cloth_id=one.id).order_by("color","guige","specs")
                    for one1 in orderClothLine:
                        samp={}
                        samp['cloth_cat'] = one.cloth_cat
                        samp['cloth_name'] = one.cloth_name
                        samp['color'] = one1.color
                        samp['color_num'] = one1.color_num
                        samp['guige'] = one1.guige
                        samp['specs'] = one1.specs
                        if one1.is_inspect:
                            samp['is_inspect'] = one1.is_inspect
                        else:
                            samp['is_inspect'] = one.is_inspect
                        samp['inspect_content'] = one1.inspect_content
                        samp['drop_status'] = orderObj.is_sure_drop_lable
                        samp['plan_start_date'] = plan_start_date
                        samp['down_day'] = down_day
                        samp['order_cloth_line_id'] = one1.id
                        samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                temp["orderObj"] = model_to_dict(orderObj)
                planOrderLine = PlanOrderLine.objects.filter(order_id=nid,delete_time=None)
                lable_drop_num = 0
                for one2 in planOrderLine:
                    if one2.drop_url:
                        lable_drop_num += 1
                    if one2.lable_url:
                        lable_drop_num += 1
                temp["cloth_cat_list"] = list(set(cloth_cat_list))
                temp["cloth_name_list"] =  list(set(cloth_name_list))
                temp["lable_drop_num"] = planOrderLine.count() * 2
                temp["lable_drop_sure_num"] = lable_drop_num

                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应洗标吊牌"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class dropLableView(APIView):
    # 添加/编辑 发货方案
    @csrf_exempt
    def post(self, request):
        sn = "2040104,2040204"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = dropSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = dropLableOneSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            bObj = PlanOrderLine.objects.get(id=done['order_line_id'])
                        except:
                            msg = "[order_line_id]参数错误"
                            error_code = 10030
                            request = request.method + '  ' + request.get_full_path()
                            post_result = {
                                "error_code": error_code,
                                "message": msg,
                                "request": request,
                            }
                            return Response(post_result)
                        bObj.update_time = dt
                        try:
                            bObj.drop_url = done["drop_url"]
                        except:
                            pass
                        try:
                            bObj.lable_url = done["lable_url"]
                        except:
                            pass
                        bObj.save()

                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                orderLineObj = PlanOrderLine.objects.filter(order_id = data['order_id'])
                drop_status = 1
                line_drop_status = []
                for one1 in orderLineObj:
                    samp = {}
                    if one1.lable_url and one1.drop_url:
                        samp['drop_status'] = 1
                    else:
                        drop_status = 0
                        samp['drop_status'] = 0
                    samp['order_line_id'] = one1.id
                    line_drop_status.append(samp)
                msg = "创建/编辑洗标吊牌"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                    "drop_status":drop_status,
                    "line_drop_status":line_drop_status,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class dropLableOneView(APIView):
    # 获取订单 发货方案
    @csrf_exempt
    def get(self, request, nid):
        sn = "2040104,2040204"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        # valObj = dropGetOneSerializer(data=request.query_params)
        try:
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            sub_data = []
            for one in orderLine:
                samp = {}
                samp["order_line_id"] = one.id
                samp['drop_url'] = one.drop_url
                samp["lable_url"] = one.lable_url
                samp["custom_type"] = one.custom_type
                samp["order_custom"] = one.order_custom
                if one.drop_url and one.lable_url:
                    samp['status'] = 1
                else:
                    samp['status'] = 0
                sub_data.append(samp)

            temp = {}
            temp['sub_data'] = sub_data
            temp['order_id'] = nid
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "获取数据失败"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



############################订单管理-采购管理###############################################

class purchasRecordsView(APIView):
    # 添加采购管理发货记录记录
    @csrf_exempt
    def post(self, request):
        sn = "20303"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg =[]
        order_cloth_line_ship_id = data['order_cloth_line_ship_id']
        if not isinstance(order_cloth_line_ship_id,int):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认发货方式Id正确！"
            samp['key_num'] = "order_cloth_line_ship_id"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num+1
            valObj = purchasRecordsSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp ={}
                samp['msg']= valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag==0:
            for done in data:
                try:
                    try:
                        mid = done["id"]
                        if mid:
                            bObj = PurchasingRecords.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = PurchasingRecords()
                            bObj.create_time = dt
                    except:
                        bObj = PurchasingRecords()
                        bObj.create_time = dt
                    bObj.order_cloth_line_ship_id = order_cloth_line_ship_id
                    bObj.send_time = done['send_time']
                    bObj.up_short_send_num = done['up_short_send_num']
                    bObj.send_num = done['send_num']
                    bObj.delivery_type = done['delivery_type']
                    bObj.delivery_name = done['delivery_name']
                    bObj.short_send_num = done['short_send_num']
                    bObj.add_up_num = done['add_up_num']
                    bObj.take_over_time = done['take_over_time']
                    bObj.take_over_num = done['take_over_num']
                    bObj.save()
                    ocslObj = OrderClothLineShip.objects.get(id=order_cloth_line_ship_id)
                    ocslObj.add_up_num = done['add_up_num']
                    ocslObj.short_send_num = done['short_send_num']
                    ocslObj.save()
                except:
                    msg = l_msg
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "创建在建企划-企划"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def delete(self, request):
        sn = "20303"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = PurchasingRecords.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "发货记录删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "发货记录不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class purchasRecordsOneView(APIView):
    @csrf_exempt
    def get(self, request, nid):
        sn = "20303"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            try:
                purch_records_id = request.query_params['purch_records_id']
            except:
                purch_records_id = 0
            lineShipObj = OrderClothLineShip.objects.get(id=nid)
            purchasObj = PurchasingRecords.objects.filter(delete_time=None,order_cloth_line_ship_id=nid)
            if purch_records_id:
                purchasObj = purchasObj.filter(id=purch_records_id)
            cObj = purchasObj.values()
            for one in cObj:
                if one["take_over_url"]:
                    one["take_over_url"] = eval(one["take_over_url"])
                if one["send_over_url"]:
                    one["send_over_url"] = eval(one["send_over_url"])

            orderObj = PlanOrder.objects.get(id=lineShipObj.order_id)
            temp = {}
            temp["data"] = cObj
            lineshipdic = model_to_dict(lineShipObj)
            if not lineshipdic["add_up_num"]:
                lineshipdic["add_up_num"] = 0
            if not lineshipdic['short_send_num']:
                if not lineshipdic['provide_num']:
                    lineshipdic['provide_num'] = 0
                lineshipdic['short_send_num'] = lineshipdic['provide_num'] - lineshipdic["add_up_num"]
            temp["lineShipObj"] = lineshipdic
            short_overflow_num, short_overflow = getOverflow(lineShipObj.order_id)
            temp['short_overflow_num'] = short_overflow_num
            temp['short_overflow'] = short_overflow * 100
            temp['order_custom'] = orderObj.custom
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的收发货记录"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def put(self, request, nid):
        sn = "20303"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            valObj = purchasRecordsUploadSerializer(data=request.data)
            if valObj.is_valid():
                purchasObj = PurchasingRecords.objects.get(id=nid)
                file_tye = int(data['file_type'])
                num1 = len(data['file_url'])
                if file_tye == 1:

                    purchasObj.take_over_url = data['file_url']
                    purchasObj.take_over_url_num = num1
                if file_tye == 2:
                    purchasObj.send_over_url = data['file_url']
                    purchasObj.send_over_url_num = num1
                purchasObj.save()
                temp = {}
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            else:
                msg = valObj.errors
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        except:
            msg = "未找到对应的收发货记录"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################订单管理-面辅料入库###############################################


class shipmentInStockView(APIView):
    # 添加/编辑 面辅料入库
    @csrf_exempt
    def post(self, request):
        sn = "20303,2040101,2040201,30102"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = shipmentInStockOneSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = shipmentInStockSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
                subdata = done['sub_data']
                s_flag = 0
                s_num = 0
                for sdone in subdata:
                    s_num = s_num + 1
                    valObjline = shipmentInStockLineShipSerializer(data=sdone)
                    if not valObjline.is_valid():
                        s_flag = 1
                        samp = {}
                        samp['msg'] = valObjline.errors
                        samp['key_num'] = s_num
                        l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############面辅料入库#############################
            if d_flag == 0 and s_flag == 0:
                for done in dataone:
                    try:
                        try:
                            bObj = OrderClothShip.objects.get(id=done['order_cloth_ship_id'])
                        except:
                            msg = "参数错误"
                            error_code = 10030
                            request = request.method + '  ' + request.get_full_path()
                            post_result = {
                                "error_code": error_code,
                                "message": msg,
                                "request": request,
                            }
                            return Response(post_result)

                        bObj.supplier = done['supplier']
                        bObj.delivery_name = done['delivery_name']
                        bObj.save()
                        # 保存面辅料的sku
                        subdata = done['sub_data']
                        for sub in subdata:
                            try:
                                sbObj = OrderClothLineShip.objects.get(id=sub["order_cloth_ship_line_id"])

                            except:
                                msg = "参数错误"
                                error_code = 10030
                                request = request.method + '  ' + request.get_full_path()
                                post_result = {
                                    "error_code": error_code,
                                    "message": msg,
                                    "request": request,
                                }
                                return Response(post_result)
                            sbObj.buy_for_num = sub['buy_for_num']
                            sbObj.short_send_num = sub['short_send_num']
                            sbObj.add_up_num = sub['add_up_num']
                            sbObj.save()

                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "创建/编辑面辅料采购"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class shipmentInStockOneView(APIView):
    # 获取订单 发货方案
    @csrf_exempt
    def get(self, request, nid):
        sn = "20303,2040101,2040201,30102"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                cloth_cat = valObj.data['cloth_cat'] if valObj.data['cloth_cat'] is not None else ""
                cloth_name = valObj.data['cloth_name'] if valObj.data['cloth_name'] is not None else ""
                supplier = valObj.data['supplier'] if valObj.data['supplier'] is not None else ""
                orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
                orderClothShip = OrderClothShip.objects.filter(delete_time=None,order_id=nid).order_by("order_cloth_id","supplier")
                if cloth_cat:
                    orderClothShip = orderClothShip.filter(cloth_cat = cloth_cat)
                if cloth_name:
                    orderClothShip = orderClothShip.filter(cloth_name=cloth_name)
                if supplier:
                    orderClothShip = orderClothShip.filter(supplier=supplier)
                samplist=[]
                for one in orderClothShip:
                    samp={}
                    samp['cloth_type'] = one.cloth_type
                    samp['cloth_cat'] = one.cloth_cat
                    samp['cloth_name'] = one.cloth_name
                    samp['delivery_type'] = one.delivery_type
                    samp['delivery_name'] = one.delivery_name
                    samp['is_inspect'] = one.is_inspect
                    samp['buy_all_num'] = one.buy_all_num
                    samp['loss_lv'] = one.loss_lv
                    samp['supplier'] = one.supplier
                    samp['plan_start_time'] = '2020-03-18'
                    samp['down_day'] = 3
                    samp['order_cloth_ship_id'] = one.id
                    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=one.order_cloth_id,order_cloth_ship_id=one.id).order_by('color', 'specs')
                    sure_num = 0
                    no_sure_num = 0
                    rObjList = rObj.values()
                    for one in rObjList:
                        if one["is_sure"] == 1:
                            sure_num = sure_num + 1
                        else:
                            no_sure_num = no_sure_num + 1
                        time1 = datetime.now()
                        try:
                            one['down_time'] = downDay(time1,one["provide_time"])
                            if one['down_time'] < 1:
                                one['down_time'] = 0
                        except:
                            one['down_time'] = 0
                    samp['sure_num'] = sure_num
                    samp['no_sure_num'] = no_sure_num
                    samp['sub_data'] = rObjList

                    samplist.append(samp)
                # 上手倒计时
                plan_start_date,down_day = getPlanStartdate(nid)
                temp = {}
                temp["data"] = samplist
                temp["orderObj"] = model_to_dict(orderObj)
                temp["plan_start_date"] = plan_start_date
                temp["down_day"] = down_day
                # 面辅料确认
                order_cloth_num, order_cloth_sure_num = getClothSureNum(nid)
                temp["order_cloth_num"] = order_cloth_num
                temp["order_cloth_sure_num"] = order_cloth_sure_num
                # 面辅料入库
                order_cloth_store_num, order_cloth_store_sure_num = getClothInStore(nid)
                temp["order_cloth_store_num"] = order_cloth_store_num
                temp["order_cloth_store_sure_num"] = order_cloth_store_sure_num
                # 检索类别
                cloth_cat_list, supplier_list, delivery_name_list = getClothCat(nid)
                temp["cloth_cat_list"] = cloth_cat_list
                temp["supplier_list"] = supplier_list
                temp["delivery_name_list"] = delivery_name_list
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的发货方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



############################生产管理-生产准备###############################################


class productReadyView(APIView):
    # 添加/编辑 生产准备
    @csrf_exempt
    def post(self, request):
        # sn = "301"
        # ret, msg = checkPermission(request, sn)
        # if ret == False:
        #     msg = msg
        #     error_code = 10001
        #     request = request.method + '  ' + request.get_full_path()
        #     post_result = {
        #         "error_code": error_code,
        #         "message": msg,
        #         "request": request,
        #     }
        #     return Response(post_result)
        data = request.data
        try:
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = productReadySerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############面辅料入库#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            bObj = FactoryMake.objects.get(id=done['factory_make_id'])
                        except:
                            msg = "参数错误"
                            error_code = 10030
                            request = request.method + '  ' + request.get_full_path()
                            post_result = {
                                "error_code": error_code,
                                "message": msg,
                                "request": request,
                            }
                            return Response(post_result)
                        try:
                            bObj.plan_start_date = done['plan_start_date']
                        except:
                            pass
                        try:
                            bObj.real_start_date = done['real_start_date']
                        except:
                            pass
                        bObj.save()
                        # 保存order数据
                        planOrderObj = PlanOrder.objects.get(id =bObj.order_id)
                        bObjLine = FactoryMake.objects.filter(order_id = bObj.order_id)
                        plan_start_date_list = []
                        real_start_date_list = []
                        real_flag = 1
                        for fc1 in bObjLine:
                            if fc1.plan_start_date:
                                plan_start_date_list.append(fc1.plan_start_date)
                            if fc1.real_start_date:
                                real_start_date_list.append(fc1.real_start_date)
                            else:
                                real_flag = 0
                        if plan_start_date_list:
                            planOrderObj.plan_start_date = min(plan_start_date_list)
                        if real_flag and real_start_date_list:
                            planOrderObj.real_start_date = min(real_start_date_list)
                        planOrderObj.save()

                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "编辑生产准备成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        except:
            msg = "系统繁忙！"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取订单 生产准备
    @csrf_exempt
    def get(self, request):
        sn = "301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = productReadyoneSerializer(data=request.query_params)
        if valObj.is_valid():
            start, page_size, flag = zddpaginate(int(valObj.data['page']), int(valObj.data['page_size']))
            if not flag:
                msg = "访问页码错误，请确认"
                error_code = 10100
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            result = []
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                make_factory = valObj.data['make_factory'] if valObj.data['make_factory'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                if brand:
                    rObj = rObj.filter(brand=brand)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if make_factory:
                    mkObj = FactoryMake.objects.filter(make_factory=make_factory)
                    oids = [one.order_id for one in mkObj]
                    rObj = rObj.filter(id__in=oids)
                # 根据实际上手日期检索
                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:]
                    data = []
                    i = 0
                    for one in rObj:
                        if i!=page_size:
                            samp = {}
                            # 发货倒计时
                            try:
                                orderlineObj = PlanOrderLine.objects.filter(order_id=one.id)
                                time1 = datetime.now()
                                send_time = orderlineObj[0].send_time
                                for one1 in orderlineObj:
                                    if send_time > one1.send_time:
                                        send_time = one1.send_time
                                samp["send_time"] = downDay(time1, send_time)
                            except:
                                samp["send_time"] = 0
                            # 上手日期处理
                            down_data = 0
                            down_list = []
                            dtnow = datetime.now()
                            fmObj = FactoryMake.objects.filter(order_id=one.id)
                            zamp = {}
                            samp["fm_num"] = fmObj.count()
                            if fmObj.count() > 0:
                                samp['factory_make_id'] = fmObj[0].id
                            else:
                                samp['factory_make_id'] = None
                            sure_plan_num = 0
                            sure_real_num = 0
                            for one2 in fmObj:
                                if one2.plan_start_date:
                                    sure_plan_num = sure_plan_num + 1
                                    down_data = downDay(one2.plan_start_date, dtnow)
                                    down_list.append(down_data)
                                if one2.real_start_date:
                                    sure_real_num = sure_real_num + 1
                            if sure_real_num != fmObj.count() or sure_plan_num != fmObj.count():
                                samp["sure_plan_num"] = sure_plan_num
                                samp["sure_real_num"] = sure_real_num
                            samp['order_id'] = one.id
                            samp['plan_id'] = one.plan_id
                            samp['create_time'] = one.create_time
                            samp['price_code'] = one.price_code
                            samp['dhkhao'] = one.dhkhao
                            samp['work_type'] = one.work_type
                            samp['leader'] = one.leader
                            #发货倒计时
                            try:
                                orderlineObj = PlanOrderLine.objects.filter(order_id = one.id,delete_time=None)
                                time1 = datetime.now()
                                send_time = orderlineObj[0].send_time
                                for one1 in orderlineObj:
                                    if send_time > one1.send_time:
                                        send_time = one1.send_time
                                samp["send_time"] = downDay(time1, send_time)
                            except:
                                samp["send_time"] = 0
                            # 上手日期处理
                            down_data=0
                            down_list = []
                            dtnow = datetime.now()
                            fmObj = FactoryMake.objects.filter(order_id=one.id)
                            zamp = {}
                            samp["fm_num"] = fmObj.count()
                            if fmObj.count()>0:
                                samp['factory_make_id'] = fmObj[0].id
                            else:
                                samp['factory_make_id'] = None
                            sure_plan_num = 0
                            sure_real_num = 0
                            for one2 in fmObj:
                                if one2.plan_start_date:
                                    sure_plan_num = sure_plan_num + 1
                                    down_data = downDay(one2.plan_start_date,dtnow)
                                    down_list.append(down_data)
                                if one2.real_start_date:
                                    sure_real_num = sure_real_num + 1
                            samp["sure_plan_num"] = sure_plan_num
                            samp["sure_real_num"] = sure_real_num
                            # zamp["fmObjLine"] = fmObj.values()
                            # samp["fmObj"] = zamp
                            if down_list:
                                samp["down_day"] = min(down_list)
                            else:
                                samp["down_day"] = None

                            # 上手倒计时
                            plan_start_date, down_day = getPlanStartdate(one.id)
                            real_start_date, down_day = getRealStartdate(one.id)
                            samp['plan_start_date'] = plan_start_date
                            samp['real_start_date'] = real_start_date

                            # 注意事项
                            notes_sure_num = 0
                            orderNotes = OrderNotes.objects.filter(order_id=one.id)
                            notes_all_num = orderNotes.count()
                            for one3 in orderNotes:
                                if one3.is_sure == 1:
                                    notes_sure_num = notes_sure_num+1
                            samp["notes_all_num"] = notes_all_num
                            samp["notes_sure_num"] = notes_sure_num
                            #确认入库
                            orderCloth = OrderCloth.objects.filter(order_id = one.id)
                            samp["order_cloth_num"] = orderCloth.count()
                            order_cloth_sure_num = 0
                            for one4 in orderCloth:
                                if one4.is_sure_in_store==1:
                                    order_cloth_sure_num += 1
                            samp["order_cloth_sure_num"] = order_cloth_sure_num
                            # 装箱要求
                            samp['pack_all_num'] = orderlineObj.count()
                            samp['pack_sure_num'] =OrderLinePacking.objects.filter(order_id = one.id).count()
                            # 订单状态
                            samp['order_type'] = "生产中"
                            data.append(samp)
                            i = i+1
                        else:
                            break
                    temp = {}
                    temp["data"] = data
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = []
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class productReadyOneView(APIView):
    # 获取订单上手时间
    @csrf_exempt
    def get(self, request, nid):
        sn = "301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            planOrder =PlanOrder.objects.get(id = nid)
            fcObj = FactoryMake.objects.filter(order_id = nid)
            samplist = []
            for one in fcObj:
                samp={}
                samp["factory_make_id"] = one.id
                samp["make_factory"] = one.make_factory
                samp['leader'] = planOrder.leader
                samp['plan_start_date'] = one.plan_start_date
                samp['real_start_date'] = one.real_start_date
                samplist.append(samp)
            temp = {}
            temp["data"] = samplist
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "参数错误"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################生产管理-加工管理############################################

class makeinReadyView(APIView):
    # 添加/编辑 生产准备
    @csrf_exempt
    def post(self, request):
        sn = "302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        try:
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = productReadySerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############面辅料入库#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            bObj = FactoryMake.objects.get(id=done['factory_make_id'])
                        except:
                            msg = "参数错误"
                            error_code = 10030
                            request = request.method + '  ' + request.get_full_path()
                            post_result = {
                                "error_code": error_code,
                                "message": msg,
                                "request": request,
                            }
                            return Response(post_result)

                        bObj.plan_start_date = done['plan_start_date']
                        try:
                            bObj.real_start_date = done['real_start_date']
                        except:
                            pass
                        bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "编辑生产准备成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        except:
            msg = "系统繁忙！"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取订单 生产准备
    @csrf_exempt
    def get(self, request):
        sn = "302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = productReadyoneSerializer(data=request.query_params)
        if valObj.is_valid():
            start, page_size, flag = zddpaginate(int(valObj.data['page']), int(valObj.data['page_size']))
            if not flag:
                msg = "访问页码错误，请确认"
                error_code = 10100
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            result = []
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                make_factory = valObj.data['make_factory'] if valObj.data['make_factory'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                if brand:
                    rObj = rObj.filter(brand=brand)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if make_factory:
                    mkObj = FactoryMake.objects.filter(make_factory=make_factory)
                    oids = [one.id for one in mkObj]
                    rObj = rObj.filter(id__in=oids)
                total = rObj.count()
                zlist = []
                if rObj.count() > start:
                    rObj = rObj.all()[start:]
                    i = 0
                    for one in rObj:
                        if i <= page_size:
                            fmObj = FactoryMake.objects.filter(order_id=one.id)
                            fm_num = fmObj.count()
                            sure_plan_num = 0
                            sure_real_num = 0
                            for one2 in fmObj:
                                if one2.plan_start_date:
                                    sure_plan_num = sure_plan_num + 1
                                if one2.real_start_date:
                                    sure_real_num = sure_real_num + 1
                            if sure_real_num == fmObj.count() and sure_plan_num == fmObj.count():
                                samp = {}
                                samp['create_time'] = one.create_time
                                samp['order_id'] = one.id
                                samp['plan_id'] = one.plan_id
                                samp['dhkhao'] = one.dhkhao
                                samp['price_code'] = one.price_code
                                samp['work_type'] = one.work_type
                                samp['leader'] = one.leader
                                samp['real_start_date'] = one.real_start_date
                                samp['inspect_time'] = 3
                                # 发货倒计时
                                try:
                                    orderlineObj = PlanOrderLine.objects.filter(order_id=one.id)
                                    time1 = datetime.now()
                                    send_time = orderlineObj[0].send_time
                                    for one1 in orderlineObj:
                                        if send_time > one1.send_time:
                                            send_time = one1.send_time
                                    samp["send_time"] = downDay(time1, send_time)
                                except:
                                    samp["send_time"] = 0
                                #注意事项
                                notes_all_num, notes_sure_num = getNotesNum(order_id=one.id)
                                samp["notes_all_num"] = notes_all_num
                                samp["notes_sure_num"] = notes_sure_num
                                #装箱情况
                                pack_num, pack_sure_num = getpackNum(one.id)
                                samp["pack_num"] = pack_num
                                samp["pack_sure_num"] = pack_sure_num
                                # 面辅料确认
                                order_cloth_num, order_cloth_sure_num = getClothSureNum(one.id)
                                samp["order_cloth_num"] = order_cloth_num
                                samp["order_cloth_sure_num"] = order_cloth_sure_num
                                # 面辅料入库
                                order_cloth_store_num, order_cloth_store_sure_num = getClothInStore(one.id)
                                samp["order_cloth_store_num"] = order_cloth_store_num
                                samp["order_cloth_store_sure_num"] = order_cloth_store_sure_num
                                # 成衣样品
                                sample_num, sample_sure_num = getPlanSampleNum(one.id)
                                samp["sample_num"] = sample_num
                                samp["sample_sure_num"] = sample_sure_num
                                # 送检情况
                                samp['inspect_num'] = 1
                                samp['inspect_sure_num'] = 1
                                # B品情况
                                samp['b_goods_num'] = 1

                                samp['order_type'] = "生产准备中"

                                zlist.append(samp)
                        else:
                            break
                    temp = {}
                    temp["data"] = zlist
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = []
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################生产管理-录入送检情况############################################

class submissionView(APIView):
    # 添加/编辑 录入送检情况
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = subMissionSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############录入送检情况#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = Submission.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = Submission()
                                bObj.create_time = dt
                        except:
                            bObj = Submission()
                            bObj.create_time = dt

                        bObj.order_id = done['order_id']
                        bObj.order_line_id = done['order_line_id']
                        bObj.submis_people = done['submis_people']
                        bObj.kuan_hao = done['kuan_hao']
                        bObj.custom = done['custom']
                        bObj.start_num = done['start_num']
                        bObj.end_num = done['end_num']
                        bObj.box_num = done['box_num']
                        bObj.color = done['color']
                        bObj.size1 = done['size1']
                        bObj.size2 = done['size2']
                        bObj.size3 = done['size3']
                        bObj.number = done['number']
                        bObj.total = done['total']
                        bObj.gross_weight = done['gross_weight']
                        bObj.net_weight = done['net_weight']
                        bObj.volume = done['volume']
                        bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "编辑录入送检情况"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        except:
            msg = "系统繁忙！"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class submissionOneView(APIView):
    # 获取订单 录入送检情况
    @csrf_exempt
    def get(self, request, nid):
        try:
            orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            if orderLine.count()>0:
                samplist=[]
                for one in orderLine:
                    submisObj = Submission.objects.filter(delete_time=None,order_line_id=one.id).order_by('kuan_hao', 'custom','start_num','end_num','box_num')
                    samp={}
                    samp['order_line_id'] = one.id
                    rObj = submisObj.values()
                    samp['sub_data'] = rObj.values()
                    samplist.append(samp)

            temp = {}
            temp["data"] = samplist
            temp["orderObj"] = model_to_dict(orderObj)
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的发货方案"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def delete(self, request,nid):
        try:
            bObj = Submission.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "送检情况删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "送检情况不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################生产管理-录入送检情况############################################

class submissionInfoView(APIView):
    # 添加/编辑 录入送检情况
    @csrf_exempt
    def post(self, request):
        data = request.query_params
        valObj = submisInfoSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            dt = datetime.now()
            ##############录入送检情况#############################
            bObj = SubmissionInfo()
            bObj.create_time = dt
            bObj.info = data['info']
            bObj.order_line_id = data['order_line_id']
            bObj.factory_name = data['factory_name']
            bObj.save()
            msg = "录入送检情况明细"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class submissionInfoOneView(APIView):
    # 获取订单 录入送检情况
    @csrf_exempt
    def put(self, request, nid):
        try:
            data = request.query_params
            valObj = submisInfoSerializer(data=request.query_params)
            if valObj.is_valid():
                result = []
                dt = datetime.now()
                ##############录入送检情况#############################
                bObj = SubmissionInfo.objects.get(id=nid)
                bObj.update_time = dt
                bObj.info = data['info']
                bObj.order_line_id = data['order_line_id']
                bObj.factory_name = data['factory_name']
                bObj.save()
                msg = "录入送检情况明细"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)

            else:
                msg = valObj.errors
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        except:
            msg = "未找到对应的订单项的资源"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def delete(self, request,nid):
        try:
            bObj = SubmissionInfo.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "送检情况删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "送检情况不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def get(self, request, nid):
        try:
            subinfo = SubmissionInfo.objects.filter(delete_time=None, order_line_id=nid)
            temp = {}
            if subinfo.count()>0:
                temp["subinfo"] = subinfo.values()
            else:
                temp["subinfo"] = []
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的送检明细"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-指示发货日期###############################################

class indicateDateView(APIView):
    # 添加/编辑 装箱指示
    @csrf_exempt
    def post(self, request):
        sn = "401"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        try:
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = request.data
            for done in dataone:
                d_num = d_num + 1
                valObjline = indicateDateoneSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存装箱指示#############################
            if d_flag == 0:
                for done in dataone:
                    try:
                        mid = done["order_id"]
                        if mid:
                            bObj = PlanOrder.objects.get(id=mid)
                            bObj.indicate_time = done['indicate_time']
                            bObj.indicate_flag = str(done['indicate_flag'])
                            bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                msg = "编辑指示发货日期"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        except:
            msg = "参数错误"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取订单 生产准备
    @csrf_exempt
    def get(self, request):
        sn = "401"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = indicateDateSerializer(data=request.query_params)
        if valObj.is_valid():
            start, page_size, flag = zddpaginate(int(valObj.data['page']), int(valObj.data['page_size']))
            if not flag:
                msg = "访问页码错误，请确认"
                error_code = 10100
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            result = []
            try:
                rObj = PlanOrder.objects.filter(delete_time=None).order_by("-indicate_flag","indicate_time","id")
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                # 未指示发货日期的订单数量
                orderNinObj = rObj.filter(indicate_time = None)
                n_num = orderNinObj.count()
                if order_type:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(order_custom=order_custom)
                if dhkhao:
                    rObj = rObj.filter(dhkhao = dhkhao)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start + page_size]
                    rObj = rObj.values()
                    for o1 in rObj:
                        orderLine = PlanOrderLine.objects.filter(order_id=o1["id"])
                        d1 = orderLine[0].send_time
                        for o2 in orderLine:
                            if d1>o2.send_time:
                                d1 = o2.send_time
                        o1["send_time"] = d1
                        o1['order_status'] = "订单状态"
                        if o1["indicate_flag"] == None:
                            o1["indicate_flag"] = "0"
                    temp = {}
                    temp["data"] = rObj
                    temp["n_num"] = n_num
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = []
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################颜色规格信息############################################

class colorSizeDataView(APIView):
    # 添加/编辑 颜色规格信息
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = colorSizeDataSerializer(data=request.data)
        if valObj.is_valid():
            result = []
            dt = datetime.now()
            ##############录入订单信息#############################
            bObj = OrderColorSizeInfo.objects.filter(order_id=data['order_id'])
            if bObj.count()>0:
                bObj = bObj[0]
            else:
                bObj = OrderColorSizeInfo()
            bObj.order_id = data['order_id']
            flag = data['flag']
            if flag==1:
                bObj.order_color_size_info = data['order_color_size_info']
            if flag ==2:
                bObj.packing_info = data['packing_info']
            bObj.save()
            # 更改装箱要求的状态
            try:
                ppObj = OrderLinePacking.objects.filter(order_id=data['order_id'])
                for one in ppObj:
                    one.status = 2
                    one.save()
            except:
                pass
            msg = "统一按照订单录入颜色规格相关信息"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class colorSizeDataOneView(APIView):
    # 获取订单 颜色规格信息
    @csrf_exempt
    def get(self, request, nid):
        try:
            subinfo = OrderColorSizeInfo.objects.filter(order_id=nid)
            temp = {}
            if subinfo.count()>0:
                temp["color_size"] = subinfo[0].order_color_size_info
                temp['packing_info'] = subinfo[0].packing_info
            else:
                temp["color_size"] = ""
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的颜色规格信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-预定仓位###############################################

class reightSpaceView(APIView):
    # 添加/编辑 预定仓位
    @csrf_exempt
    def post(self, request):
        sn = "402"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        dataone = request.data
        for done in dataone:
            d_num = d_num + 1
            valObjline = reightSpaceobjSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    order_line_id =done['order_line_id']
                    planLine = PlanOrderLine.objects.get(id=order_line_id)
                    if done['reightspace_flag']!=-1:
                        bObj = ReightSpace.objects.filter(reightspace_flag=done['reightspace_flag'])
                        if bObj.count()>0:
                            bObj = bObj[0]
                            temp = json.loads(bObj.order_line_ids)
                            if done['order_line_id'] not in temp:
                                temp.append(done['order_line_id'])
                                bObj.order_line_ids = temp
                                bObj.save()
                        else:
                            temp = []
                            temp.append(done['order_line_id'])
                            bObj = ReightSpace()
                            bObj.create_time = dt
                            bObj.indicate_time = done['indicate_time']
                            bObj.reightspace_flag = done["reightspace_flag"]
                            bObj.exporter_way = planLine.exporter_way
                            bObj.pol = planLine.pol
                            bObj.pod = planLine.pod
                            bObj.transportation = planLine.transportation
                            bObj.order_line_ids = temp
                            bObj.status = 0
                            bObj.save()
                        planLine.reight_space_id =bObj.id
                    else:
                        bObj = ReightSpace.objects.filter(reightspace_flag=planLine.reightspace_flag)
                        if bObj.count() > 0:
                            bObj = bObj[0]
                            temp = json.loads(bObj.order_line_ids)
                            temp.remove(done['order_line_id'])
                            bObj.order_line_ids = temp
                            bObj.save()
                        planLine.reight_space_id = None
                    planLine.reightspace_flag = done['reightspace_flag']
                    planLine.save()

                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑指示预定仓位"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取预定仓位
    @csrf_exempt
    def get(self, request):
        sn = "402"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = reightSpaceLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None,order_type__in=[1,2])
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                order_ids = [one.id for one in rObj]
                orderLine = PlanOrderLine.objects.filter(delete_time=None,order_id__in=order_ids,order_type__in=[1,3]).order_by("-reight_space_id","order_id")
                temp = {}
                data = orderLine.values()
                for one in data:
                    orderObj = PlanOrder.objects.get(id=one["order_id"])
                    if one["reight_space_id"]:
                        onespcace = ReightSpace.objects.get(id=one["reight_space_id"])
                        one["reight_space_status"] = onespcace.status
                        one['indicate_time'] = onespcace.indicate_time
                        one['pod'] = onespcace.pod
                        one['pol'] = onespcace.pol
                        one['exporter_way'] = onespcace.exporter_way
                        one['transportation'] = onespcace.transportation
                        one['info_url'] = onespcace.info_url
                        one['reight_s_time'] = onespcace.reight_s_time
                    else:
                        one["reight_space_status"] = 0
                        one['indicate_time'] = orderObj.indicate_time
                        one['info_url'] = None
                        one['reight_s_time'] = None
                    one['dhkhao'] = orderObj.dhkhao
                    one['price_code'] = orderObj.price_code
                    one['order_status'] = "订单状态"

                temp["data"] = data
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class reightSpaceOneView(APIView):
    # 获取预定仓位
    @csrf_exempt
    def get(self, request, nid):
        sn = "402"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            rObj = ReightSpace.objects.get(id=nid)
            ids = rObj.order_line_ids.split(",")
            orderLine = PlanOrderLine.objects.filter(delete_time=None,id__in=ids).order_by("-reight_space_id","order_id")
            zemp = []
            for one in orderLine:
                orderObj = PlanOrder.objects.get(id=one.order_id)
                samp = {}
                samp['order_custom'] = one.order_custom
                samp['dhkhao'] = orderObj.dhkhao
                samp['price_code'] = orderObj.price_code
                samp['brand'] = orderObj.brand
                samp['goods_name'] = orderObj.goods_name
                samp['indicate_time'] = orderObj.indicate_time
                samp['warehouse_time'] = one.warehouse_time
                samp['pol'] = rObj.pol
                samp['pod'] = rObj.pod
                samp['price_terms'] = one.price_terms
                packObj = OrderPackInfo.objects.filter(order_line_id=one.id)
                if packObj.count()>0:
                    samp['volume'] = packObj[0].volume
                    samp['pack_weight'] = packObj[0].pack_weight
                    samp['unit_weight'] = packObj[0].unit_weight
                    samp['box_pack_num'] = packObj[0].box_pack_num
                    samp['order_num'] = packObj[0].order_num
                    samp['box_num'] = packObj[0].box_num
                    samp['predict_volume'] = packObj[0].predict_volume
                    samp['order_rough_weight'] = packObj[0].order_rough_weight
                    samp['order_net_weight'] = packObj[0].order_net_weight
                else:
                    samp['volume'] = None
                    samp['pack_weight'] = None
                    samp['unit_weight'] = None
                    samp['box_pack_num'] = None
                    samp['order_num'] = None
                    samp['box_num'] = None
                    samp['predict_volume'] = None
                    samp['order_rough_weight'] = None
                    samp['order_net_weight'] = None
                zemp.append(samp)
            temp = {}
            temp["data"] = zemp
            temp['shou_huo_term_name'] = rObj.shou_huo_term_name
            temp['space_name'] = rObj.space_name
            temp['exporter_way'] = rObj.exporter_way
            temp['reight_space_id'] =nid
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的仓位信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 批量删除 订单出货方案showOutStock
    @csrf_exempt
    def delete(self, request, nid):
        sn = "402"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            bObj = ReightSpace.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "仓位信息删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "仓位信息不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
    #
    @csrf_exempt
    def post(self, request, nid):
        sn = "402"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        valObj = reightSpaceOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                dt = datetime.now()
                bObj = ReightSpace.objects.get(id=nid)
                bObj.update_time = dt
                bObj.reight_s_time = request.query_params["reight_s_time"]
                bObj.info_url =request.query_params["info_url"]
                bObj.status = 1
                bObj.save()
                msg = "确认预定仓位"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "id参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 预定仓位
    @csrf_exempt
    def put(self, request, nid):
        valObj = reightSpaceOne1Serializer(data=request.query_params)
        if valObj.is_valid():
            try:
                dt = datetime.now()
                bObj = ReightSpace.objects.get(id=nid)
                bObj.update_time = dt
                bObj.shou_huo_term_name = request.query_params["shou_huo_term_name"]
                bObj.space_name = request.query_params["space_name"]
                bObj.save()
                # 更改进仓日
                line_id = bObj.order_line_ids
                try:
                    line_id_list = json.loads(line_id)
                    for o1 in line_id_list:
                        orderlne = PlanOrderLine.objects.get(id = o1)
                        orderlne.warehouse_time = request.query_params["warehouse_time"]
                        orderlne.save()
                except:
                    pass
                msg = "确认预定仓位"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "id参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-报关理单###############################################

class exportCustomsDeclarationView(APIView):
    # 获取报关理单
    @csrf_exempt
    def get(self, request):
        sn = "403"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = exportCustomsDeclarationSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None,order_type__in=[1,2])
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                bill= valObj.data['bill'] if valObj.data['bill'] is not None else ""
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                order_ids = [one.id for one in rObj]
                orderLine = PlanOrderLine.objects.filter(delete_time=None,order_id__in=order_ids).order_by("-reight_space_id","order_id")
                temp = {}
                data = orderLine.values()
                for one in data:
                    orderObj = PlanOrder.objects.get(id=one["order_id"])
                    if one["reight_space_id"]:
                        onespcace = ReightSpace.objects.get(id=one["reight_space_id"])
                        one["reight_space_status"] = onespcace.status
                        one['indicate_time'] = onespcace.indicate_time
                        one['pod'] = onespcace.pod
                        one['pol'] = onespcace.pol
                        one['exporter_way'] = onespcace.exporter_way
                        one['transportation'] = onespcace.transportation
                    else:
                        one["reight_space_status"] = 0
                        one['indicate_time'] = orderObj.indicate_time
                    one['dhkhao'] = orderObj.dhkhao
                    one['price_code'] = orderObj.price_code
                    # 获取送检报告
                    mfi_num, mfi_y_num = getMakeFatoryInspect(one["order_id"])
                    one["mfi_num"] = mfi_num
                    one["mfi_y_num"] = mfi_y_num

                    # 确认报关和结算
                    pxObj = PlanClothSampleLine.objects.filter(plan_id=orderObj.plan_id,delete_time=None,is_pay=1, send_custom=one["order_custom"])
                    pcsl_num = pxObj.count()
                    pcsl_sure_num = 0
                    for o2 in pxObj:
                        if o2.is_sure == 1:
                            pcsl_sure_num +=1
                    one["pcsl_num"] = pcsl_num
                    one["pcsl_sure_num"] = pcsl_sure_num

                    one["custom_dec_num"] = 1
                    one["custom_dec_y_num"] = 1

                    one["export_info_num"] = 1
                    one["export_info_y_num"] = 1
                    one['order_status'] = "订单状态"

                temp["data"] = data
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



# 样品
class exportClothSampleView(APIView):
    # 样品
    @csrf_exempt
    def get(self, request, nid):
        sn = "403010101,403010201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            orderLine = PlanOrderLine.objects.get(id=nid)
            order = PlanOrder.objects.get(id=orderLine.order_id)
            pclsObj = PlanClothSampleLine.objects.filter(plan_id=order.plan_id, delete_time=None,is_pay=1, send_custom=orderLine.order_custom)
            temp = {}
            temp["data"] = pclsObj.values()
            temp['order_custom'] = orderLine.order_custom
            temp['provide_custom'] ="南通风尚国际"
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的仓位信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################生产管理-录入工厂送检情况###############################################

class makeFactoryInspectView(APIView):
    # 添加/编辑 录入工厂送检情况
    @csrf_exempt
    def post(self, request):
        sn = "30205"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = inspectSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = inspectOneSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            datains = data['inspect_name_list']
            d_i_flag = 0
            d_i_num = 0
            l_i_msg = []
            dataone = data['data']
            for dione in datains:
                d_num = d_num + 1
                valObjiline = inspectInOneSerializer(data=dione)
                if not valObjline.is_valid():
                    d_i_flag = 1
                    samp = {}
                    samp['msg'] = valObjiline.errors
                    samp['key_i_num'] = d_i_num
                    l_i_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0 and d_i_flag ==0:
                for dione in datains:
                    mfObj = FactoryMake.objects.get(id=dione['make_factory_id'])
                    mfObj.inspect_name = dione['inspect_name']
                    mfObj.save()
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = MakeFatoryInspect.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = MakeFatoryInspect()
                                bObj.create_time = dt
                        except:
                            bObj = MakeFatoryInspect()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        bObj.dhkh = done["dhkh"]
                        bObj.custom = done["custom"]
                        bObj.order_line_id = done["order_line_id"]
                        bObj.make_factory_id =done["make_factory_id"]
                        bObj.make_factory = done["make_factory"]
                        bObj.box_hao_start = done['box_hao_start']
                        bObj.box_hao_end = done["box_hao_end"]
                        bObj.box_num = done["box_num"]
                        bObj.box_hao_type = done["box_hao_type"]
                        bObj.color = done["color"]
                        temp = []
                        bObj.specs = done["specs_list"]
                        bObj.num = done["num"]
                        bObj.total = done["total"]
                        bObj.gw = done["gw"]
                        bObj.nw = done["nw"]
                        bObj.meas = done["meas"]
                        bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.inspect_name = data['inspect_name']
                    order.save()
                except:
                    pass
                msg = "创建/编辑工厂送检成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                msg1 = l_i_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "message1": msg1,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class makeFactoryInspectOneView(APIView):
    # 获取录入工厂送检情况
    @csrf_exempt
    def get(self, request, nid):
        sn = "30205"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            factoryObj = FactoryMake.objects.filter(order_id=nid)
            order_color_list = []
            order_specs_list = []
            custom_list = []
            comments=""
            # 检品数据
            fm_list = []
            try:
                overflow_num = order.order_num - order.contract_num
            except:
                overflow_num = 0
            for one in factoryObj:
                fm_dic = {}
                fm_dic['make_factory_id'] = one.id
                fm_dic['make_factory'] = one.make_factory
                fm_dic['inspect_name'] = one.inspect_name
                order_line_list = []
                # 订单项数据
                for one1 in orderLine:
                    comments += one1.comments
                    custom_list.append(one1.order_custom)
                    order_line_dic = {}
                    order_line_dic['order_custom'] = one1.order_custom
                    order_line_dic['order_line_id'] = one1.id
                    #颜色尺码数据
                    color_list = []
                    specs_list = []
                    ousStock = OutStock.objects.filter(order_id=nid,order_line_id=one1.id)
                    for one2 in ousStock:
                        if one2.color not in color_list:
                            color_list.append(one2.color)
                        if one2.specs not in specs_list:
                            s_spes = {}
                            s_spes[str(one2.specs)] = one2.specs
                            specs_list.append(s_spes)
                        if one2.color not in order_color_list:
                            order_color_list.append(one2.color)
                        if one2.specs not in order_specs_list:
                            order_specs_list.append(one2.specs)
                    order_line_dic['color_list'] =color_list
                    order_line_dic['specs_list'] = specs_list
                    #装箱信息
                    orderPackInfo = OrderPackInfo.objects.filter(order_line_id = one1.id)
                    if orderPackInfo.count()>0:
                        order_line_dic['box_rough_weight'] = orderPackInfo[0].box_rough_weight
                        order_line_dic['box_pack_num'] = orderPackInfo[0].box_pack_num
                        order_line_dic['pack_weight'] = orderPackInfo[0].pack_weight
                        order_line_dic['unit_weight'] = orderPackInfo[0].unit_weight
                        order_line_dic['volume'] = orderPackInfo[0].volume

                    else:
                        order_line_dic['box_rough_weight'] =None
                        order_line_dic['box_pack_num'] = None
                        order_line_dic['pack_weight'] = None
                        order_line_dic['unit_weight'] = None
                        order_line_dic['volume'] = None
                    # 已保存数据
                    mkfacObj = MakeFatoryInspect.objects.filter(order_id=nid,make_factory_id=one.id,order_line_id=one1.id).order_by("color")
                    if mkfacObj.count()>0:
                        order_line_dic["inspect_info"]= mkfacObj.values()
                    else:
                        zamp = {}
                        zamp['id'] = 0
                        zamp['custom'] = one1.order_custom
                        zamp['order_id'] = order.id
                        zamp['make_factory_id'] = one.id
                        zamp['order_line_id'] = one1.id
                        zamp['make_factory'] = one.make_factory
                        zamp['box_hao_start'] = None
                        zamp['box_hao_end'] = None
                        zamp['box_hao_type'] = None
                        zamp['box_num'] = None
                        zamp['color'] = None
                        zamp['specs'] = specs_list
                        zamp['num'] = None
                        zamp['total'] = None
                        zamp['gw'] = None
                        zamp['nw'] = None
                        zamp['meas'] = None
                        llist = []
                        llist.append(zamp)
                        order_line_dic["inspect_info"] = llist

                    order_line_list.append(order_line_dic)
                fm_dic['order_line_info'] = order_line_list
                fm_list.append(fm_dic)
            temp = {}
            temp["data"] = fm_list
            temp['comments'] = comments
            temp['orderObj'] = model_to_dict(order)
            temp['overflow_num'] = overflow_num
            temp['custom_list'] = custom_list
            temp['order_color_list'] = order_color_list
            temp['order_specs_list'] = order_specs_list
            temp['order_specs_list_num'] = len(order_specs_list)
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)

        except:
            msg = "未找到对应的厂送检情况"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 批量删除 订单出货方案showOutStock
    @csrf_exempt
    def delete(self, request, nid):
        sn = "30205"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            bObj = MakeFatoryInspect.objects.get(id=nid)
            bObj.delete()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "工厂送检情况删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "工厂送检情况不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def post(self, request, nid):
        sn = "30205"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        valObj = inspectinfoUrlSerializer(data=request.query_params)
        if valObj.is_valid():
            type = valObj.data['type'] if valObj.data['type'] is not None else 1
            file_url = valObj.data['file_url'] if valObj.data['file_url'] is not None else ""
            if type ==1:
                bObj = FactoryMake.objects.get(id=nid)
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "data":model_to_dict(bObj),
                    "error_code": error_code,
                    "message": "工厂送检明细单保存成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                bObj = FactoryMake.objects.get(id=nid)
                bObj.inspect_url = file_url
                bObj.save()
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "工厂送检明细单保存成功!",
                    "request": request,
                }
                return Response(post_result)

        else:
            msg = "工厂送检情况不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################订单管理-报关理单###############################################

class inportCustomsDeclarationView(APIView):
    # 添加/编辑 国内出货理单
    @csrf_exempt
    def post(self, request):
        sn = "40302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        dataone = request.data
        for done in dataone:
            d_num = d_num + 1
            valObjline = inportCustomsDeclarationsaveSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid = done['order_line_id']
                    if mid:
                        bObj = PlanOrderLine.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.indicate_time = done['indicate_time']
                        bObj.delivery_way = done['delivery_way']
                        bObj.delivery_time = done['delivery_time']
                        bObj.save()
                except:
                    msg = "order_line_id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑指示预定仓位"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 获取国内出货理单
    @csrf_exempt
    def get(self, request):
        sn = "40302"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = exportCustomsDeclarationSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None,order_type__in=[3])
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                bill= valObj.data['bill'] if valObj.data['bill'] is not None else ""
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                order_ids = [one.id for one in rObj]
                orderLine = PlanOrderLine.objects.filter(delete_time=None,order_id__in=order_ids).order_by("-reight_space_id","order_id")
                temp = {}
                data = orderLine.values()
                for one in data:
                    orderObj = PlanOrder.objects.get(id=one["order_id"])
                    if not one['indicate_time']:
                        one['indicate_time'] = orderObj.indicate_time
                    one['dhkhao'] = orderObj.dhkhao
                    one['price_code'] = orderObj.price_code
                # 获取送检报告
                    mfi_num, mfi_y_num = getMakeFatoryInspect(one["order_id"])
                    one["mfi_num"] = mfi_num
                    one["mfi_y_num"] = mfi_y_num
                    one['order_status'] = "订单状态"
                temp["data"] = data
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



############################生产管理-包箱信息###############################################

class PackInfoView(APIView):
    # 添加/编辑 包箱信息
    @csrf_exempt
    def post(self, request):
        sn = "30202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = PackInfoSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            try:
                try:
                    mid = data["order_line_id"]
                    orderPackInfo = OrderPackInfo.objects.filter(order_line_id=mid)
                    if orderPackInfo.count()>0:
                        bObj = orderPackInfo[0]
                        bObj.update_time = dt
                    else:
                        bObj = OrderPackInfo()
                        bObj.create_time = dt
                except:
                    bObj = OrderPackInfo()
                    bObj.create_time = dt
                bObj.extent = data['extent']
                bObj.height = data['height']
                bObj.width = data['width']
                bObj.volume = data['volume']
                bObj.order_num = data['order_num']
                bObj.box_num = data['box_num']
                bObj.box_pack_num = data['box_pack_num']
                bObj.predict_volume = data['predict_volume']
                bObj.pack_weight = data['pack_weight']
                bObj.unit_weight = data['unit_weight']
                bObj.box_rough_weight = data['box_rough_weight']
                bObj.order_net_weight = data['order_net_weight']
                bObj.order_rough_weight = data['order_rough_weight']
                bObj.order_line_id = data['order_line_id']
                bObj.save()
            except:
                msg = "参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            try:
                # 更新order
                order = PlanOrder.objects.get(id=data['order_id'])
                order.inspect_name = data['inspect_name']
                order.save()
            except:
                pass
            msg = "创建/编辑包装规格重量、装箱信息"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class PackInfoOneView(APIView):
    # 包箱信息
    @csrf_exempt
    def get(self, request, nid):
        sn = "30202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            orderLine = PlanOrderLine.objects.get(id=nid)
            orderPackInfo = OrderPackInfo.objects.filter(order_line_id = nid)
            packlineOne = OrderLinePacking.objects.filter(order_line_id = nid)
            temp = {}
            if orderPackInfo.count()>0:
                temp["data"] = model_to_dict(orderPackInfo[0])
            else:
                temp["data"] = {}
                if not orderLine.order_num:
                    temp['data']['order_num'] = 0
                else:
                    temp['data']['order_num'] = orderLine.order_num
            temp['order_num'] = orderLine.order_num
            temp['order_line_id'] = orderLine.id
            if packlineOne.count()>0:
                temp['specs'] = packlineOne[0].specs
                temp['scale'] = packlineOne[0].scale
            else:
                temp['specs'] =None
                temp['scale'] = None
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应包箱信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################生产管理-B品管理###############################################

class BqualityView(APIView):
    # 添加/编辑 包箱信息
    @csrf_exempt
    def post(self, request):
        sn = "30206"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = BqualitySerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            type = data['type']
            order_id = data['order_id']
            factory_make_id = data['factory_make_id']
            if type == 1:
                facObj = FactoryMake.objects.get(id = factory_make_id)
                facObj.is_b_sure = 1
                facObj.b_num = 0
                facObj.save()
            elif type == 0:
                try:
                    b_num = 0
                    for done in data['data']:
                        b_num += done['b_num']
                        faclineObj = FactoryMakeLine.objects.get(id=done['factory_make_line_id'])
                        faclineObj.b_num = done['b_num']
                        faclineObj.inspect_num = done['inspect_num']
                        faclineObj.recover_b_num = done['recover_b_num']
                        faclineObj.save()
                    facObj = FactoryMake.objects.get(id=factory_make_id)
                    facObj.is_b_sure = 1
                    facObj.b_num = b_num
                    facObj.save()
                except:
                    msg = "参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            else:
                msg = "type取值为0，1"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)


            msg = "录入工厂B品回收数量"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class BqualityOneView(APIView):
    # b品数量
    @csrf_exempt
    def get(self, request, nid):
        sn = "30206"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = getBqualitySerializer(data=request.query_params)
        if valObj.is_valid():
            tyep = valObj.data['type']
            facObj = FactoryMake.objects.get(id=nid)
            zamp = []
            temp = {}
            if type == 1:
                outObj = OutStock.objects.filter(order_id = facObj.order_id,delete_time=None).order_by("color_name","color_num","specs")
                for one in outObj:
                    f_make_line = FactoryMakeLine.objects.filter(order_id=facObj.order_id, factory_make_id=nid,
                                                                 color_name=one.color_name, color_num=one.color_num,
                                                                 specs=one.specs)
                    make_num = 0
                    b_num = 0
                    inspect_num = 0
                    recover_b_num = 0
                    for o in f_make_line:
                        if o.make_num:
                            make_num = make_num + o.make_num
                        if o.inspect_num:
                            inspect_num = inspect_num + o.inspect_num
                        if o.recover_b_num:
                            recover_b_num = recover_b_num + o.recover_b_num
                        if o.b_num:
                            b_num = b_num + o.b_num
                    samp = {}
                    samp['out_stock_id'] = one.id
                    samp['order_line_id'] = 0
                    samp['factory_make_line_id'] = 0
                    samp['order_id'] = facObj.order_id
                    samp['color_name'] = one.color_name
                    samp['color_num'] = one.color_num
                    samp['specs'] = one.specs
                    samp['b_num'] = b_num
                    samp['inspect_num'] = inspect_num
                    samp['recover_b_num'] = recover_b_num
                    samp['make_num'] = make_num
                    zamp.append(samp)
            else:
                f_make_line = FactoryMakeLine.objects.filter(factory_make_id=nid).order_by("order_line_id","color_name","color_num","specs")
                for one in f_make_line:
                    samp = {}
                    samp['out_stock_id'] = 0
                    samp['order_line_id'] = one.order_line_id
                    samp['factory_make_line_id'] = one.id
                    samp['order_id'] = one.order_id
                    samp['color_name'] = one.color_name
                    samp['color_num'] = one.color_num
                    samp['specs'] = one.specs
                    samp['b_num'] = one.b_num
                    samp['inspect_num'] = one.inspect_num
                    samp['recover_b_num'] = one.recover_b_num
                    samp['make_num'] = one.make_num
                    zamp.append(samp)
            temp['bObj'] = zamp
            temp['order_id'] = facObj.order_id
            temp['factory_make_id'] = int(nid)
            temp['factory_b_num'] = facObj.b_num
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        else:
            msg = "未找到对应加工工厂信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)




############################合同管理###############################################

class showContractView(APIView):
    # 添加/编辑 包箱信息
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = showContractSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            try:
                try:
                    type = data["type"]
                    contractObj = Contracts.objects.filter(type=type)
                    if contractObj.count()>0:
                        bObj = contractObj[0]
                        bObj.update_time = dt
                    else:
                        bObj = Contracts()
                        bObj.create_time = dt
                except:
                    bObj = Contracts()
                    bObj.create_time = dt
                bObj.merchant_id = data['merchant_id']
                bObj.type = data['type']
                bObj.items = data['items']
                bObj.save()
            except:
                msg = "参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            msg = "创建/编辑 合同模板"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class showContractOneView(APIView):
    # 包箱信息
    @csrf_exempt
    def get(self, request, nid):
        try:
            orderLine = PlanOrderLine.objects.get(id=nid)
            orderPackInfo = OrderPackInfo.objects.filter(order_line_id = nid)
            packlineOne = OrderLinePacking.objects.filter(order_line_id = nid)
            temp = {}
            if orderPackInfo.count()>0:
                temp["data"] = model_to_dict(orderPackInfo[0])
            else:
                temp["data"] = {}
            temp['order_num'] = orderLine.order_num
            temp['orderLine'] = model_to_dict(orderLine)
            if packlineOne.count()>0:
                temp['specs'] = packlineOne[0].specs
                temp['scale'] = packlineOne[0].scale
            else:
                temp['specs'] =None
                temp['scale'] = None
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应包箱信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################报关管理-录入工厂送检情况###############################################

class exportFactoryInspectView(APIView):
    # 添加/编辑 录入工厂送检情况
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = inspectSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = exportinspectOneSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            datains = data['inspect_name_list']
            d_i_flag = 0
            d_i_num = 0
            l_i_msg = []
            dataone = data['data']
            for dione in datains:
                d_num = d_num + 1
                valObjiline = inspectInOneSerializer(data=dione)
                if not valObjline.is_valid():
                    d_i_flag = 1
                    samp = {}
                    samp['msg'] = valObjiline.errors
                    samp['key_i_num'] = d_i_num
                    l_i_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0 and d_i_flag ==0:
                inspect_name = ""
                for dione in datains:
                    mfObj = FactoryMake.objects.get(id=dione['make_factory_id'])
                    mfObj.inspect_name = dione['inspect_name']
                    mfObj.save()
                    inspect_name = dione['inspect_name']
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = MakeFatoryInspect.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = MakeFatoryInspect()
                                bObj.create_time = dt
                        except:
                            bObj = MakeFatoryInspect()
                            bObj.create_time = dt
                        bObj.specs = done["specs_list"]
                        bObj.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.inspect_name = inspect_name
                    order.export_goods_name = data['export_goods_name']
                    order.inport_goods_name = data['inport_goods_name']
                    order.inspect_send_info_person = data['inspect_send_info_person']
                    order.save()
                except:
                    pass
                msg = "创建/编辑工厂送检成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                msg1 = l_i_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "message1": msg1,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class exportFactoryInspectOneView(APIView):
    # 获取录入工厂送检情况
    @csrf_exempt
    def get(self, request, nid):
        try:
            order = PlanOrder.objects.get(id=nid)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            factoryObj = FactoryMake.objects.filter(order_id=nid)
            order_color_list = []
            order_specs_list = []
            custom_list = []
            comments=""
            # 检品数据
            fm_list = []
            for one in factoryObj:
                fm_dic = {}
                fm_dic['make_factory_id'] = one.id
                fm_dic['make_factory'] = one.make_factory
                fm_dic['inspect_name'] = one.inspect_name
                order_line_list = []
                # 订单项数据
                for one1 in orderLine:
                    comments += one1.comments
                    custom_list.append(one1.order_custom)
                    order_line_dic = {}
                    order_line_dic['order_custom'] = one1.order_custom
                    order_line_dic['order_line_id'] = one1.id
                    #颜色尺码数据
                    color_list = []
                    specs_list = []
                    ousStock = OutStock.objects.filter(order_id=nid,order_line_id=one1.id)
                    for one2 in ousStock:
                        if one2.color not in color_list:
                            color_list.append(one2.color)
                        if one2.specs not in specs_list:
                            specs_list.append(one2.specs)
                        if one2.color not in order_color_list:
                            order_color_list.append(one2.color)
                        if one2.specs not in order_specs_list:
                            order_specs_list.append(one2.specs)
                    order_line_dic['color_list'] =color_list
                    order_line_dic['specs_list'] = specs_list
                    #装箱信息
                    orderPackInfo = OrderPackInfo.objects.filter(order_line_id = one1.id)
                    if orderPackInfo.count()>0:
                        order_line_dic['box_rough_weight'] = orderPackInfo[0].box_rough_weight
                        order_line_dic['box_pack_num'] = orderPackInfo[0].box_pack_num
                        order_line_dic['pack_weight'] = orderPackInfo[0].pack_weight
                        order_line_dic['unit_weight'] = orderPackInfo[0].unit_weight
                        order_line_dic['volume'] = orderPackInfo[0].volume

                    else:
                        order_line_dic['box_rough_weight'] =None
                        order_line_dic['box_pack_num'] = None
                        order_line_dic['pack_weight'] = None
                        order_line_dic['unit_weight'] = None
                        order_line_dic['volume'] = None
                    # 已保存数据
                    mkfacObj = MakeFatoryInspect.objects.filter(order_id=nid,make_factory_id=one.id,order_line_id=one1.id).order_by("color")
                    # if mkfacObj.count()>0:
                    order_line_dic["inspect_info"]= mkfacObj.values()
                    # else:
                    #     zamp = {}
                    #     zamp['id'] = 0
                    #     zamp['custom'] = one1.order_custom
                    #     zamp['order_id'] = order.id
                    #     zamp['make_factory_id'] = one.id
                    #     zamp['order_line_id'] = one1.id
                    #     zamp['make_factory'] = one.make_factory


                    order_line_list.append(order_line_dic)
                fm_dic['order_line_info'] = order_line_list
                fm_list.append(fm_dic)
            temp = {}
            temp["data"] = fm_list
            temp['comments'] = comments
            temp['orderObj'] = model_to_dict(order)
            temp['custom_list'] = custom_list
            temp['order_color_list'] = order_color_list
            temp['order_specs_list'] = order_specs_list
            temp['order_specs_list_num'] = len(order_specs_list)
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)

        except:
            msg = "未找到对应的厂送检情况"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 批量删除 订单出货方案showOutStock
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = MakeFatoryInspect.objects.get(id=nid)
            bObj.delete()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "工厂送检情况删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "工厂送检情况不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def post(self, request, nid):
        valObj = inspectinfoUrlSerializer(data=request.query_params)
        if valObj.is_valid():
            type = valObj.data['type'] if valObj.data['type'] is not None else 1
            file_url = valObj.data['file_url'] if valObj.data['file_url'] is not None else ""
            if type ==1:
                bObj = FactoryMake.objects.get(id=nid)
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "data":model_to_dict(bObj),
                    "error_code": error_code,
                    "message": "工厂送检明细单保存成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                bObj = FactoryMake.objects.get(id=nid)
                bObj.inspect_url = file_url
                bObj.save()
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "工厂送检明细单保存成功!",
                    "request": request,
                }
                return Response(post_result)

        else:
            msg = "工厂送检情况不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



############################账目管理-订单应收--确认报价###############################################

class orderAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "5010101,5010102"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                rObj = PlanOrder.objects.filter(delete_time=None)
                if status  == 0:
                    rObj = rObj.filter(~Q(sure_status=1))
                if status ==1:
                    rObj = rObj.filter(sure_status=1)
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if brand:
                    rObj = rObj.filter(brand=brand)

                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["brand"] = one.brand
                    zamp["goods_name"] = one.goods_name
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    orderline = PlanOrderLine.objects.filter(order_id=one.id)
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_price ==1:
                            c_pay_sure_num +=1
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    otherPay = OrderPay.objects.filter(order_id=one.id)
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_price == 1:
                            other_pay_sure_num +=1
                    zamp["other_pay_num"] = other_pay_num
                    zamp["other_pay_sure_num"] = other_pay_sure_num
                    zamp["status"] = status
                    zamp["order_status"] = "订单状态"
                    samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class orderAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "501010101,501010201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            planOrder = PlanOrderLine.objects.filter(order_id=nid)
            zemp = []
            order_sn = ""
            for one in planOrder:
                samp = {}
                order_sn = order_sn + one.order_sn + "|"
                samp['order_type'] = one.order_type
                samp['custom'] = one.order_custom
                samp['provide_custom'] = "南通风尚国际"
                samp['order_line_id'] = one.id
                samp["goods_name"] = order.goods_name
                outstock = OutStock.objects.filter(order_line_id=one.id,delete_time=None).order_by("color","specs")
                order_all_num = 0
                for one1 in outstock:
                    order_all_num +=one1.order_num
                samp['out_stock_date'] = outstock.values()
                plansample = PlanClothSampleLine.objects.filter(plan_id=order.plan_id,sample_type="船样")
                samp['sample_shipping'] = plansample.count()
                planprice = PlanPrice.objects.get(plan_id=order.plan_id)
                samp['price_type'] = planprice.price_type
                samp['price_rate'] = planprice.price_rate
                samp['plan_price'] = planprice.plan_price
                if one.is_shipping:
                    samp['is_shipping'] = one.is_shipping
                else:
                    samp['is_shipping'] = 0
                if  one.order_price_type:
                    samp['order_price_type'] = one.order_price_type
                else:
                    samp['order_price_type'] = planprice.price_type
                if one.order_price:
                    samp['order_price'] = one.order_price
                    samp['amount'] = order_all_num * one.order_price
                else:
                    samp['order_price'] = planprice.plan_price
                    samp['amount'] = order_all_num * planprice.plan_price
                samp['is_sure_price'] =one.is_sure_price
                zemp.append(samp)
            temp = {}
            temp["data"] = zemp
            # temp['shou_huo_term_name'] = rObj.shou_huo_term_name
            # temp['space_name'] = rObj.space_name
            # temp['exporter_way'] = rObj.exporter_way
            temp['order_id'] =nid
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的仓位信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def post(self, request, nid):
        sn = "501010101,501010201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        valObj = orderAccountOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                dt = datetime.now()
                bObj = PlanOrderLine.objects.get(id=nid)
                bObj.update_time = dt
                bObj.is_shipping = request.query_params["is_shipping"]
                bObj.order_price_type =request.query_params["order_price_type"]
                bObj.order_price = request.query_params["order_price"]
                bObj.is_sure_price = request.query_params["is_sure_price"]
                bObj.save()
                # 订单是否全部确认
                # 是否确认
                orderline = PlanOrderLine.objects.filter(order_id=bObj.order_id)
                c_pay_num = orderline.count()
                c_pay_sure_num = 0
                for o1 in orderline:
                    if o1.is_sure_price == 1:
                        c_pay_sure_num += 1
                otherPay = OrderPay.objects.filter(order_id=bObj.order_id)
                other_pay_num = otherPay.count()
                other_pay_sure_num = 0
                for o2 in otherPay:
                    if o2.is_sure_price == 1:
                        other_pay_sure_num += 1

                order = PlanOrder.objects.get(id=bObj.order_id)
                if c_pay_num==c_pay_sure_num and other_pay_num==other_pay_sure_num:
                    order.sure_status = 1
                else:
                    order.sure_status = 0
                order.save()
                msg = "确认合同报价"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "id参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class orderOtherAccountsView(APIView):
    # 添加/编辑 其他应收款
    @csrf_exempt
    def post(self, request):
        sn = "501010102,501010202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data  = request.data
        try:
            order_id = data['order_id']
        except:
            msg = "请输入订单id"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        dataone =data['data']
        for done in dataone:
            d_num = d_num + 1
            valObjline = orderOtherAcountOneSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid =done['id']
                    if mid:
                        bObj = OrderPay.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = OrderPay()
                        bObj.create_time = dt
                    bObj.order_id = data['order_id']
                    bObj.custom = done['custom']
                    bObj.pay_content = done['pay_content']
                    bObj.pay_type = done['pay_type']
                    bObj.pay_num = done['pay_num']
                    bObj.pay_price = done['pay_price']
                    bObj.amount = done['amount']
                    bObj.is_sure_price = done['is_sure_price']
                    bObj.save()
                    # 订单是否全部确认
                    # 是否确认
                    orderline = PlanOrderLine.objects.filter(order_id=data['order_id'])
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_price == 1:
                            c_pay_sure_num += 1
                    otherPay = OrderPay.objects.filter(order_id=data['order_id'])
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_price == 1:
                            other_pay_sure_num += 1

                    order = PlanOrder.objects.get(id=data['order_id'])
                    if c_pay_num == c_pay_sure_num and other_pay_num == other_pay_sure_num:
                        order.sure_status = 1
                    else:
                        order.sure_status = 0
                    order.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑其他应收款"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class orderOtherAccountsOneView(APIView):
    # 获取其他应收款
    @csrf_exempt
    def get(self, request, nid):
        sn = "501010102,501010202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            orderPay = OrderPay.objects.filter(delete_time = None,order_id = nid)
            custom_dic, custom_list = getAllCustom(nid)
            temp = {}
            temp["data"] = orderPay.values()
            temp['order_type'] =order.order_type
            temp['provide'] = "南通风尚国际"
            temp['order_type'] = order.order_type
            temp['dhkhao'] = order.dhkhao
            temp['price_code'] = order.price_code
            temp['custom_list'] = custom_list
            temp['custom_dic'] = custom_dic
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "确认其他应收款"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 批量删除 其他应收款
    @csrf_exempt
    def delete(self, request, nid):
        sn = "501010102,501010202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            bObj = OrderPay.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他应收款信息删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "其他应收款不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class orderInAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "5010201,5010202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderInAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                search_time_type = valObj.data['search_time_type'] if valObj.data['search_time_type'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else ""
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else ""
                invoice_num = valObj.data['invoice_num'] if valObj.data['invoice_num'] is not None else ""
                fee_num = valObj.data['fee_num'] if valObj.data['fee_num'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if search_time_type == 1:
                    if start_time:
                        rObj = rObj.filter(create_time__gte=start_time)
                    if end_time:
                        rObj = rObj.filter(create_time__lte=end_time)
                if search_time_type == 2:
                    if start_time:
                        rObj = rObj.filter(indicate_time__gte = start_time)
                    if end_time:
                        rObj = rObj.filter(indicate_time__lte = end_time)
                if invoice_num:
                    rObj = rObj.filter(invoice_num=invoice_num)
                if fee_num:
                    rObj = rObj.filter(fee_num__in=fee_num)
                if status:
                    if status !=1:
                        rObj = rObj.filter(~Q(is_finish_pay=1))
                    else:
                        rObj = rObj.filter(is_finish_pay=1)
                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["invoice_num"] = one.invoice_num
                    zamp["fee_num"] = one.fee_num
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    fee_no = ""
                    orderline = PlanOrderLine.objects.filter(order_id=one.id)
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_price == 1:
                            c_pay_sure_num += 1
                            if o1.fee_no:
                                fee_no += o1.fee_no + "|"
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    otherPay = OrderPay.objects.filter(order_id=one.id)
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_price == 1:
                            other_pay_sure_num += 1
                        if o2.fee_no:
                            fee_no += o2.fee_no + "|"
                    zamp["other_pay_num"] = other_pay_num
                    zamp["other_pay_sure_num"] = other_pay_sure_num
                    pay_finish_deg, pay_status, all_amount, pay_amount = orderPayStatus(one.id)
                    zamp["pay_finish_deg"] = pay_finish_deg
                    zamp["pay_status"] = pay_status
                    zamp["all_amount"] = all_amount
                    zamp["pay_amount"] = pay_amount
                    zamp['fee_no'] = fee_no
                    zamp["order_status"] = "订单状态"
                    zamp["status"] = status
                    samp.append(zamp)
                temp = {}
                pay_info = getOrderPayNum()
                temp["data"] = samp
                temp['order_pay_info'] = pay_info
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 新增订单收款结算
    @csrf_exempt
    def post(self, request):
        sn = "5010201,5010202,5010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data  = request.data
        try:
            order_id = data['order_id']
        except:
            msg = "请输入订单id"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        dataone =data['data']
        for done in dataone:
            d_num = d_num + 1
            valObjline = orderInAccountsOneSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid = done['id']
                    if mid:
                        bObj = OrderPayInfoList.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = OrderPayInfoList()
                        bObj.create_time = dt
                    bObj.order_id = data['order_id']
                    bObj.custom = done['custom']
                    bObj.custom_type = done['custom_type']
                    bObj.price_type = done['price_type']
                    bObj.pay_amount = done['pay_amount']
                    bObj.pay_y_amount = done['pay_y_amount']
                    bObj.pay_n_amount_one = done['pay_n_amount_one']
                    bObj.beizhun = done['beizhun']
                    bObj.order_line_id = done['order_line_id']
                    bObj.order_other_pay_id = done['order_other_pay_id']
                    bObj.save()
                    # 订单是否全部确认
                    if done['order_line_id']:
                        orderline = PlanOrderLine.objects.get(id=done['order_line_id'])
                        payInfo = OrderPayInfoList.objects.filter(delete_time=None,order_line_id=done['order_line_id'])
                        amount = orderline.order_price
                        y_amount = Decimal(0)
                        for o1 in payInfo:
                            y_amount = y_amount +o1.pay_amount
                        if orderline.order_price == y_amount:
                            orderline.is_finish_pay = 1
                        orderline.pay_y_amount = y_amount
                        orderline.pay_n_amount = amount-y_amount
                        orderline.save()
                    if done['order_other_pay_id']:
                        orderPay = OrderPay.objects.get(id=done['order_other_pay_id'])
                        payInfo = OrderPayInfoList.objects.filter(delete_time=None, order_other_pay_id=done['order_other_pay_id'])
                        amount = orderPay.amount
                        y_amount = Decimal(0)
                        for o2 in payInfo:
                            y_amount = y_amount + o2.pay_amount
                        if orderPay.amount == y_amount:
                            orderPay.is_finish_pay = 1
                        orderPay.pay_y_amount = y_amount
                        orderPay.pay_n_amount = amount-y_amount
                        orderPay.save()

                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "保存收款结算信息"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 发货方案
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = OrderPayInfoList.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "收款结算删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "收款结算不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

################################### 订单收款结算###############################
class orderInAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "5010201,5010202,5010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.query_params
            try:
                account_type = int(data['account_type'])
                order_line_id = int(data['order_line_id'])
                order_other_pay_id = int(data['order_other_pay_id'])
            except:
                account_type = 0
            order = PlanOrder.objects.get(id=nid)
            if account_type==0:
                planOrder = PlanOrderLine.objects.filter(order_id=nid)
                orderPay = OrderPay.objects.filter(order_id=nid)
                orderPayInfoList = OrderPayInfoList.objects.filter(delete_time=None, order_id=nid)
            elif account_type ==1:
                planOrder = PlanOrderLine.objects.filter(order_id=nid,id=order_line_id)
                orderPay = []
                orderPayInfoList = OrderPayInfoList.objects.filter(delete_time=None, order_id=nid,order_line_id=order_line_id)
            elif account_type ==2:
                planOrder = []
                orderPay = OrderPay.objects.filter(id=order_other_pay_id)
                orderPayInfoList = OrderPayInfoList.objects.filter(delete_time=None, order_id=nid,order_other_pay_id = order_other_pay_id)
            zemp = []
            order_sn = ""
            for one in planOrder:
                samp = {}
                order_sn = order_sn + one.order_sn +"|"
                samp['custom'] = one.order_custom
                samp['custom_flag'] = 1
                samp['price_type'] = one.order_price_type
                samp['amount'] = one.order_price
                samp['pay_y_amount'] = one.pay_y_amount
                samp['pay_n_amount'] = one.pay_n_amount
                samp['order_id'] = nid
                samp['order_line_id'] = one.id
                samp['order_other_pay_id'] = 0
                zemp.append(samp)
            for one2 in orderPay:
                samp = {}
                samp['custom'] = one2.custom
                samp['custom_flag'] = 1
                samp['price_type'] = one2.pay_type
                samp['amount'] = one2.amount
                samp['pay_y_amount'] = one2.pay_y_amount
                samp['pay_n_amount'] = one2.pay_n_amount
                samp['order_id'] = nid
                samp['order_line_id'] = 0
                samp['order_other_pay_id'] = one.id
                zemp.append(samp)
            # 结算列表信息

            data = orderPayInfoList.values()
            for o3 in data:
                if o3["order_line_id"]:
                    lineone = PlanOrderLine.objects.get(id=o3["order_line_id"])
                    o3['pay_y_amount'] = lineone.pay_y_amount
                if o3["order_other_pay_id"]:
                    orderpay = OrderPay.objects.get(id=o3["order_other_pay_id"])
                    o3['pay_y_amount'] = orderpay.pay_y_amount
            temp = {}
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp["data"] = orderPayInfoList.values()
            temp["payData"] = zemp
            temp['order_id'] =nid
            custom_dic, custom_list = getAllCustom(nid)
            temp["custom_dic"] = custom_dic
            temp['custom_list'] = custom_list
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的仓位信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def put(self, request, nid):
        sn = "5010201,5010202,5010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            dt = datetime.now()
            # 订单项
            order = PlanOrder.objects.get(id=nid)
            order.is_finish_pay = 1
            order.save()
            orderLine = PlanOrderLine.objects.filter(order_id = nid)
            for one in orderLine:
                one.is_finish_pay = 1
                one.save()
                payInfo = OrderPayInfoList.objects.filter(order_line_id = one.id)
                y_l_amount = Decimal(0)
                for o1 in payInfo:
                    y_l_amount += o1.pay_amount
                if one.order_price == y_l_amount:
                    one.is_finish_pay = 1
                    one.save()
                else:
                    msg = "存在不一致的结算数据"
                    error_code = 0
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            payOther = OrderPay.objects.filter(order_id = nid)
            for one1 in payOther:
                one1.is_finish_pay = 1
                one1.save()
                payInfo = OrderPayInfoList.objects.filter(order_other_pay_id=one1.id)
                y_o_amount = Decimal(0)
                for o2 in payInfo:
                    y_o_amount += o2.pay_amount
                if one1.amount == y_o_amount:
                    one1.is_finish_pay = 1
                    one1.save()
                else:
                    msg = "存在不一致的结算数据"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "确认全部收款完成"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "id参数错误"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


###################################应收账目明细################################

class orderInAllAccountsView(APIView):
    # 获取应收账目明细
    @csrf_exempt
    def get(self, request):
        sn = "5010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderInAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                merchant_name = "南通风尚国际"
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                search_time_type = valObj.data['search_time_type'] if valObj.data['search_time_type'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else ""
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else ""
                invoice_num = valObj.data['invoice_num'] if valObj.data['invoice_num'] is not None else ""
                fee_num = valObj.data['fee_num'] if valObj.data['fee_num'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if search_time_type == 1:
                    if start_time:
                        rObj = rObj.filter(create_time__gte=start_time)
                    if end_time:
                        rObj = rObj.filter(create_time__lte=end_time)
                if search_time_type == 2:
                    if start_time:
                        rObj = rObj.filter(indicate_time__gte = start_time)
                    if end_time:
                        rObj = rObj.filter(indicate_time__lte = end_time)
                if invoice_num:
                    rObj = rObj.filter(invoice_num=invoice_num)
                if fee_num:
                    rObj = rObj.filter(fee_num__in=fee_num)
                if status:
                    if status != 1:
                        rObj = rObj.filter(~Q(is_finish_pay=1))
                    else:
                        rObj = rObj.filter(is_finish_pay=1)
                samp = []
                for one in rObj:
                    # 订单应收
                    orderLine = PlanOrderLine.objects.filter(order_id=one.id)
                    for order in orderLine:
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        #
                        zamp['merchant_name'] = merchant_name
                        zamp["price_type"] = order.order_price_type
                        zamp["order_price"] = order.order_price
                        try:
                            zamp["pay_finish_deg"] = round(order.pay_y_amount/order.order_price,2)
                        except:
                            zamp["pay_finish_deg"] = 0
                        zamp['is_finish_pay'] = order.is_finish_pay
                        zamp['fee_no_status'] = order.fee_no_status
                        zamp["order_status"] = "订单状态"
                        zamp['account_type'] = 1
                        zamp['order_line_id'] = order.id
                        zamp["order_other_pay_id"] = 0
                        zamp['fee_no'] = order.fee_no
                        zamp["status"] = status
                        samp.append(zamp)
                    #其他应收
                    otherPay = OrderPay.objects.filter(order_id=one.id)
                    for other in otherPay:
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        #
                        zamp["price_type"] = other.pay_type
                        zamp["order_price"] = other.amount
                        try:
                            zamp["pay_finish_deg"] = round(other.pay_y_amount / other.amount, 2)
                        except:
                            zamp['pay_finish_deg'] = 0
                        zamp['is_finish_pay'] = other.is_finish_pay
                        zamp['fee_no_status'] = other.fee_no_status
                        zamp["order_status"] = "订单状态"
                        zamp['account_type'] = 2
                        zamp['order_line_id'] = 0
                        zamp["order_other_pay_id"] = other.id
                        zamp['fee_no'] = other.fee_no
                        zamp["status"] = status
                        samp.append(zamp)

                temp = {}
                pay_info = getOrderPayNum()
                temp["data"] = samp
                temp['order_pay_info'] = pay_info
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################账目管理-生产应付###############################################

class productAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "5010201,5010202,5010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                rObj = PlanOrder.objects.filter(delete_time=None)
                if status == 0:
                    rObj = rObj.filter(~Q(sure_status=1))
                if status ==1:
                    rObj = rObj.filter(sure_status=1)
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if brand:
                    rObj = rObj.filter(brand=brand)

                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["brand"] = one.brand
                    zamp["goods_name"] = one.goods_name
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    orderline = OrderClothShip.objects.filter(order_id=one.id)
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_pay == 1:
                            c_pay_sure_num += 1
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    otherPay = FactoryMake.objects.filter(order_id=one.id)
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_pay == 1:
                            other_pay_sure_num +=1
                    zamp["make_pay_num"] = other_pay_num
                    zamp["make_pay_sure_num"] = other_pay_sure_num
                    zamp["status"] = status
                    samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class productAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "502010101,502010201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
            planOrder = PlanOrderLine.objects.filter(order_id=nid)
            order_sn = ""
            for one in planOrder:
                order_sn = order_sn + one.order_sn + "|"
            fmObj = FactoryMake.objects.filter(order_id=nid)
            coop_mode = ''
            ticketing_custom = ''
            for o in fmObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            orderClothShip = OrderClothShip.objects.filter(delete_time=None, order_id=nid).order_by(
                "order_cloth_id", "supplier")
            samplist = []
            supplier_list = []
            supplier_num = orderClothShip.count()
            supplier_sure_num = 0
            for one in orderClothShip:
                if one.is_sure_pay ==1:
                    supplier_sure_num +=1
                # 供应商
                supplier_list.append(one.supplier)
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
                samp['coop_mode'] = coop_mode
                samp['ticketing_custom'] = ticketing_custom
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
                samplist.append(samp)

            temp = {}
            supplier_no_num = supplier_num - supplier_sure_num
            temp["data"] = samplist
            temp['supplier_num'] = supplier_num
            temp['supplier_sure_num'] = supplier_sure_num
            temp['supplier_no_num'] = supplier_no_num
            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = orderObj.dhkhao
            temp["price_code"] = orderObj.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = orderObj.invoice_num
            temp["fee_num"] = orderObj.fee_num
            temp["work_type"] = orderObj.work_type
            temp["supplier_list"] = list(set(supplier_list))
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的采购数据"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def post(self, request, nid):
        sn = "502010101,502010201"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        valObj = productAccountOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                dt = datetime.now()
                bObj = OrderClothLineShip.objects.get(id=nid)
                bObj.update_time = dt
                bObj.price_type = request.query_params["price_type"]
                bObj.sure_price =request.query_params["sure_price"]
                bObj.is_sure_pay = request.query_params["is_sure_pay"]
                bObj.pay_amount = request.query_params["pay_amount"]
                bObj.save()
                # 采购 是否全部确认
                orderCloth = OrderClothShip.objects.get(id = bObj.order_cloth_ship_id)
                orderClothLine = OrderClothLineShip.objects.filter(order_cloth_ship_id = bObj.order_cloth_ship_id)
                flag = 0
                pay_amount = Decimal(0)
                for one in orderClothLine:
                    if one.is_sure_pay !=1:
                        flag = 1
                    else:
                        pay_amount += one.pay_amount
                if flag == 0:
                    orderCloth.is_sure_pay = 1
                    orderCloth.save()
                    #保存付款项目
                    projectPay = ProductPayStatic.objects.filter(order_cloth_ship_id = bObj.order_cloth_ship_id)
                    if projectPay.count()>0:
                        projectOne = projectPay[0]
                    else:
                        projectOne = ProductPayStatic()
                    projectOne.order_id = orderCloth.order_id
                    projectOne.type = 1
                    projectOne.factory_make_id = 0
                    projectOne.order_cloth_ship_id = bObj.order_cloth_ship_id
                    projectOne.pay_project = "采购费"
                    projectOne.custom_type = "面辅料供应商"
                    projectOne.custom =orderCloth.supplier
                    projectOne.pay_custom = orderCloth.delivery_name
                    projectOne.pay_comment = ""
                    projectOne.price_type = orderCloth.price_type
                    projectOne.pay_price = pay_amount
                    projectOne.pay_num = 1
                    projectOne.pay_amount = pay_amount
                    projectOne.finish_amount = Decimal(0)
                    projectOne.is_sure = 1
                    projectOne.is_finish_pay = 0
                    projectOne.save()

                else:
                    orderCloth.is_sure_pay = 0
                    orderCloth.save()
                msg = "确认合同报价"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "id参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class productMakeAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = orderAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                rObj = PlanOrder.objects.filter(delete_time=None)
                if status == 0:
                    rObj = rObj.filter(~Q(sure_status=1))
                if status ==1:
                    rObj = rObj.filter(sure_status=1)
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if brand:
                    rObj = rObj.filter(brand=brand)

                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["brand"] = one.brand
                    zamp["goods_name"] = one.goods_name
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    orderline = PlanOrderLine.objects.filter(order_id=one.id)
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_price ==1:
                            c_pay_sure_num +=1
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    otherPay = OrderPay.objects.filter(order_id=one.id)
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_price == 1:
                            other_pay_sure_num +=1
                    zamp["other_pay_num"] = other_pay_num
                    zamp["other_pay_sure_num"] = other_pay_sure_num
                    zamp["status"] = status
                    samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class productMakeAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "502010102,502010202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            planPrice = PlanPrice.objects.get(plan_id =order.plan_id)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            factoryObj = FactoryMake.objects.filter(order_id=nid)
            order_sn = ""
            for o1 in orderLine:
                order_sn = order_sn + o1.order_sn + "|"

            coop_mode = ''
            ticketing_custom = ''
            for o in factoryObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            coop_mode_all = ""
            # 检品数据
            fm_list = []
            new_amount = Decimal(0)
            all_amount = Decimal(0)
            for one in factoryObj:
                fm_dic = {}
                fm_dic['make_factory_id'] = one.id
                fm_dic['make_factory'] = one.make_factory
                fm_dic['coop_mode'] = one.coop_mode
                coop_mode_all =coop_mode_all +one.coop_mode + "|"
                fm_dic['ticketing_custom'] = one.ticketing_custom
                fm_dic['price_type'] = one.price_type
                fm_dic['plan_price'] = planPrice.plan_price
                fm_dic['amount'] = one.amount
                if one.amount:
                    all_amount += one.amount
                fm_dic['sure_amount'] = one.sure_amount
                fmpObj = ProductPayStatic.objects.filter(factory_make_id=one.id)
                one_new_amount = Decimal(0)
                for o1 in fmpObj:
                    if o1.set_amount:
                        one_new_amount += o1.set_amount
                        new_amount += o1.set_amount
                        all_amount += o1.set_amount
                fm_dic['new_amount'] =one_new_amount
                order_line_list = []
                # 订单项数据
                for one1 in orderLine:
                    jamp  = {}
                    samp,zemp = getOrderFactoryInfoColor(nid,one1.id,one.id)
                    jamp['order_line_one'] = zemp
                    jamp['custom'] = one1.order_custom
                    jamp['order_type'] = one1.order_custom
                    order_line_list.append(zemp)
                fm_dic['order_line_info'] = order_line_list
                fm_list.append(fm_dic)
            temp = {}
            temp["data"] = fm_list

            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp["work_type"] = order.work_type
            temp["new_lv"] =round(new_amount/all_amount,2)
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应加工费报价"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def post(self, request, nid):
        sn = "502010102,502010202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        valObj = productMakeAccountOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                dt = datetime.now()
                bObj = FactoryMake.objects.get(id=nid)
                bObj.update_time = dt
                bObj.price_type = request.query_params["price_type"]
                bObj.make_pay_num =request.query_params["make_pay_num"]
                bObj.sure_amount = request.query_params["sure_amount"]
                bObj.amount = request.query_params["amount"]
                bObj.is_sure_pay = 1
                bObj.save()
                # 添加加工费项目
                projectPay = ProductPayStatic.objects.filter(factory_make_id=nid)
                if projectPay.count() > 0:
                    projectOne = projectPay[0]
                else:
                    projectOne = ProductPayStatic()
                projectOne.order_id = bObj.order_id
                projectOne.type = 2
                projectOne.factory_make_id = nid
                projectOne.order_cloth_ship_id = 0
                projectOne.pay_project = "加工费"
                projectOne.custom_type = "加工工厂"
                projectOne.custom = bObj.make_factory
                projectOne.pay_custom = bObj.ticketing_custom
                projectOne.pay_comment = ""
                projectOne.price_type = request.query_params["price_type"]
                projectOne.pay_price = request.query_params["sure_amount"]
                projectOne.pay_num = request.query_params["make_pay_num"]
                projectOne.pay_amount =  request.query_params["amount"]
                projectOne.finish_amount = Decimal(0)
                projectOne.is_sure = 1
                projectOne.is_finish_pay = 0
                projectOne.save()

                msg = "确认加工费报价"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "id参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
    # 报价调整
    @csrf_exempt
    def put(self, request, nid):
        sn = "502010102,502010202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            set_amount = request.query_params['set_amount']
            Obj = ProductPayStatic.objects.get(id=nid)
            Obj.set_amount = set_amount
            Obj.save()
            temp = {}
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应加工费报价"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class productOtherAccountsView(APIView):
    # 添加/编辑 生产组织其他应付
    @csrf_exempt
    def post(self, request):
        sn = "502010103,502010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data  = request.data
        try:
            order_id = data['order_id']
        except:
            msg = "请输入订单id"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        dataone =data['data']
        for done in dataone:
            d_num = d_num + 1
            valObjline = makeOtherAcountOneSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid =done['id']
                    if mid:
                        bObj = ProductPayStatic.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = ProductPayStatic()
                        bObj.create_time = dt
                    bObj.order_id = data['order_id']
                    bObj.pay_project = done['pay_project']
                    bObj.custom_type = done['custom_type']
                    bObj.custom = done['custom']
                    bObj.pay_custom = done['pay_custom']
                    bObj.pay_comment = done['pay_comment']
                    bObj.price_type = done['price_type']
                    bObj.pay_num = done['pay_num']
                    bObj.pay_price = done['pay_price']
                    bObj.pay_amount = done['pay_amount']
                    bObj.factory_make_id = 0
                    bObj.order_cloth_ship_id = 0
                    bObj.finish_amount = Decimal(0)
                    bObj.type = 3
                    bObj.is_sure = 1
                    bObj.is_finish_pay = 0
                    bObj.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑其他应收款"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 生产组织其他应付
    @csrf_exempt
    def delete(self, request):
        sn = "502010103,502010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = ProductPayStatic.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "生产组织其他应付删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "生产组织其他应付不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class productOtherAccountsOneView(APIView):
    # 获取生产组织其他应付
    @csrf_exempt
    def get(self, request, nid):
        sn = "502010103,502010203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            makePay = ProductPayStatic.objects.filter(delete_time = None,order_id = nid,type=3)
            custom_dic, custom_list = getAllCustom(nid)
            orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
            planOrder = PlanOrderLine.objects.filter(order_id=nid)
            order_sn = ""
            for one in planOrder:
                order_sn = order_sn + one.order_sn + "|"
            fmObj = FactoryMake.objects.filter(order_id=nid)
            coop_mode = ''
            ticketing_custom = ''
            for o in fmObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            temp = {}
            temp["data"] = makePay.values()
            temp['order_type'] =order.order_type
            temp['provide'] = "南通风尚国际"
            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = orderObj.dhkhao
            temp["price_code"] = orderObj.price_code
            # temp["order_sn"] = order_sn
            # temp["invoice_num"] = orderObj.invoice_num
            # temp["fee_num"] = orderObj.fee_num
            temp["work_type"] = orderObj.work_type
            temp['custom_list'] = custom_list
            temp['custom_dic'] = custom_dic
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "确认生产组织其他应付"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)




class productInALLAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "5020203"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderInAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                search_time_type = valObj.data['search_time_type'] if valObj.data['search_time_type'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else ""
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else ""
                invoice_num = valObj.data['invoice_num'] if valObj.data['invoice_num'] is not None else ""
                fee_num = valObj.data['fee_num'] if valObj.data['fee_num'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if search_time_type == 1:
                    if start_time:
                        rObj = rObj.filter(create_time__gte=start_time)
                    if end_time:
                        rObj = rObj.filter(create_time__lte=end_time)
                if search_time_type == 2:
                    if start_time:
                        rObj = rObj.filter(indicate_time__gte = start_time)
                    if end_time:
                        rObj = rObj.filter(indicate_time__lte = end_time)
                if invoice_num:
                    rObj = rObj.filter(invoice_num=invoice_num)
                if fee_num:
                    rObj = rObj.filter(custom=fee_num)
                if status:
                    rObj = rObj.filter(pay_status=status)
                samp = []
                dollor = Decimal(0)
                euro = Decimal(0)
                renminbi = Decimal(0)
                pay_order_no_num = 0
                for one in rObj:
                    # 是否确认
                    projectPay = ProductPayStatic.objects.filter(order_id=one.id,delete_time=None)
                    pay_sure_num = 0
                    fee_no = ""
                    for o1 in projectPay:
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        if o1.is_finish_pay == 1:
                            pay_sure_num += 1
                        if o1.price_type=="人民币" and o1.pay_amount and o1.finish_amount:
                            renminbi =renminbi + o1.pay_amount-o1.finish_amount
                        if o1.price_type=="美元" and o1.pay_amount and o1.finish_amount:
                            dollor =dollor + o1.pay_amount-o1.finish_amount
                        if o1.price_type=="欧元" and o1.pay_amount and o1.finish_amount:
                            euro =euro + o1.pay_amount-o1.finish_amount

                        zamp['receip_custom'] = o1.custom
                        zamp['pay_custom'] = o1.pay_custom
                        zamp['price_type'] = o1.price_type
                        zamp['pay_amount'] = o1.pay_amount
                        zamp['finish_amount'] = o1.finish_amount
                        try:
                            zamp["pay_finish_deg"] = round(o1.finish_amount / o1.pay_amount, 2)
                        except:
                            zamp["pay_finish_deg"] = 0
                        zamp['is_finish_pay'] = o1.is_finish_pay
                        zamp["status"] = "订单状态"
                        zamp["fee_no"] = o1.fee_no
                        zamp["fee_no_status"] = o1.fee_no_status
                        samp.append(zamp)

                temp = {}
                temp["data"] = samp
                temp["renminbi"] = renminbi
                temp["dollor"] = dollor
                temp["euro"] = euro
                temp["pay_order_no_num"] = pay_order_no_num
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class productInAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "5020201,5020202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderInAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                search_time_type = valObj.data['search_time_type'] if valObj.data['search_time_type'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else ""
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else ""
                invoice_num = valObj.data['invoice_num'] if valObj.data['invoice_num'] is not None else ""
                fee_num = valObj.data['fee_num'] if valObj.data['fee_num'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if search_time_type == 1:
                    if start_time:
                        rObj = rObj.filter(create_time__gte=start_time)
                    if end_time:
                        rObj = rObj.filter(create_time__lte=end_time)
                if search_time_type == 2:
                    if start_time:
                        rObj = rObj.filter(indicate_time__gte = start_time)
                    if end_time:
                        rObj = rObj.filter(indicate_time__lte = end_time)
                if invoice_num:
                    rObj = rObj.filter(invoice_num=invoice_num)
                if fee_num:
                    rObj = rObj.filter(custom=fee_num)
                if status:
                    rObj = rObj.filter(pay_status=status)
                samp = []
                dollor = Decimal(0)
                euro = Decimal(0)
                renminbi = Decimal(0)
                pay_order_no_num = 0
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["invoice_num"] = one.invoice_num
                    zamp["fee_num"] = one.fee_num
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    pay_amount = Decimal(0)
                    finish_amount = Decimal(0)
                    projectPay = ProductPayStatic.objects.filter(order_id=one.id,delete_time=None)
                    pay_sure_num = 0
                    fee_no = ""
                    for o1 in projectPay:
                        if o1.pay_amount:
                            pay_amount += o1.pay_amount
                        if o1.finish_amount:
                            finish_amount += o1.finish_amount
                        if o1.is_finish_pay == 1:
                            pay_sure_num += 1
                        if o1.price_type=="人民币" and o1.pay_amount and o1.finish_amount:
                            renminbi =renminbi + o1.pay_amount-o1.finish_amount
                        if o1.price_type=="美元" and o1.pay_amount and o1.finish_amount:
                            dollor =dollor + o1.pay_amount-o1.finish_amount
                        if o1.price_type=="欧元" and o1.pay_amount and o1.finish_amount:
                            euro =euro + o1.pay_amount-o1.finish_amount
                        if o1.fee_no:
                            fee_no += o1.fee_no + "|"
                    try:
                        zamp["pay_finish_deg"] = round(finish_amount/ pay_amount, 2)
                    except:
                        zamp["pay_finish_deg"] = 0
                    zamp['pay_num'] = projectPay.count()
                    zamp['pay_sure_num'] = pay_sure_num
                    if projectPay.count() != pay_sure_num:
                        pay_order_no_num +=1
                        zamp['is_finish_pay'] = 0
                    else:
                        zamp['is_finish_pay'] = 1
                    zamp["status"] = "订单状态"
                    zamp["fee_no"] = fee_no
                    samp.append(zamp)

                temp = {}
                temp["data"] = samp
                temp["renminbi"] = renminbi
                temp["dollor"] = dollor
                temp["euro"] = euro
                temp["pay_order_no_num"] = pay_order_no_num
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class productInAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "5020201,5020202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            planOrder = PlanOrderLine.objects.filter(delete_time=None,order_id=nid)
            mfobj = FactoryMake.objects.filter(delete_time=None,order_id=nid)

            zemp = []
            order_sn = ""
            coop_mode = ""
            ticketing_custom = ""
            for one in planOrder:
                order_sn = order_sn + one.order_sn +"|"
            for one1 in mfobj:
                coop_mode  = coop_mode + one1.coop_mode + "|"
                ticketing_custom = ticketing_custom + one1.ticketing_custom + "|"

            # 结算列表信息
            projectPay = ProductPayStatic.objects.filter(delete_time=None,order_id=nid)
            p_data = projectPay.values()
            no_num = 0
            for o in p_data:
                if o["is_finish_pay"] !=1:
                    try:
                        o["pay_finish_deg"] = round(o["finish_amount"]/ o["pay_amount"], 2)
                    except:
                        o["pay_finish_deg"] = 0
                    no_num += 1

            temp = {}
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["coop_mode"] = coop_mode
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp['work_type'] = order.work_type
            temp["data"] = projectPay.values()
            temp["merchant"] = "南通风尚国际"
            temp["ticketing_custom"] = ticketing_custom
            temp['order_id'] =nid
            custom_dic, custom_list = getAllCustom(nid)
            temp["custom_dic"] = custom_dic
            temp['custom_list'] = custom_list
            temp["account_num"] = projectPay.count()
            temp["account_finish_num"] = projectPay.count() - no_num
            temp["account_no_num"] = no_num
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的报价项目"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class productPayAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "5020201,5020202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderInAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                search_time_type = valObj.data['search_time_type'] if valObj.data['search_time_type'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else ""
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else ""
                invoice_num = valObj.data['invoice_num'] if valObj.data['invoice_num'] is not None else ""
                fee_num = valObj.data['fee_num'] if valObj.data['fee_num'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if search_time_type == 1:
                    if start_time:
                        rObj = rObj.filter(create_time__gte=start_time)
                    if end_time:
                        rObj = rObj.filter(create_time__lte=end_time)
                if search_time_type == 2:
                    if start_time:
                        rObj = rObj.filter(indicate_time__gte = start_time)
                    if end_time:
                        rObj = rObj.filter(indicate_time__lte = end_time)
                if invoice_num:
                    rObj = rObj.filter(invoice_num=invoice_num)
                if fee_num:
                    rObj = rObj.filter(custom=fee_num)
                if status:
                    rObj = rObj.filter(pay_status=status)
                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["invoice_num"] = one.invoice_num
                    zamp["fee_num"] = one.fee_num
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    projectPay = ProductPayStatic.objects.filter(order_id=one.id,delete_time=None)
                    pay_sure_num = 0
                    for o1 in projectPay:
                        if o1.is_finish_pay == 1:
                            pay_sure_num += 1
                    zamp['pay_num'] = projectPay.count()
                    zamp['pay_sure_num'] = pay_sure_num
                    zamp["status"] = "订单状态"
                    samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

     # 添加/编辑  付款操作

    @csrf_exempt
    def post(self, request):
        sn = "5020201,5020202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data = request.data
        try:
            product_pay_static_id = data['product_pay_static_id']
        except:
            msg = "请输入订单id"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        dataone = data['data']
        for done in dataone:
            d_num = d_num + 1
            valObjline = orderPayAccountsLineSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid = done['id']
                    if mid:
                        bObj = ProductPayInfo.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = ProductPayInfo()
                        bObj.create_time = dt
                    bObj.product_pay_static_id = data['product_pay_static_id']
                    bObj.price_type = done['price_type']
                    bObj.pay_mode = done['pay_mode']
                    bObj.pay_now_amount = done['pay_now_amount']
                    bObj.pay_all_amount = done['pay_all_amount']
                    bObj.pay_no_amount = done['pay_no_amount']
                    bObj.is_entrust = done['is_entrust']
                    bObj.entrust_company = done['entrust_company']
                    bObj.entrust_book = done['entrust_book']
                    bObj.save()
                    productsta = ProductPayStatic.objects.get(id= data['product_pay_static_id'])
                    infoObj = ProductPayInfo.objects.filter(product_pay_static_id=data['product_pay_static_id'])
                    amount  = Decimal(0)
                    for one in infoObj:
                        amount +=one.pay_now_amount
                    productsta.finish_amount = amount
                    if productsta.pay_amount<=amount:
                        productsta.is_finish_pay = 1
                    productsta.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑付款操作"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class productPayAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "5020201,5020202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            projectPay = ProductPayStatic.objects.get(id=nid,delete_time=None)
            order = PlanOrder.objects.get(delete_time=None,id=projectPay.order_id)
            planOrder = PlanOrderLine.objects.filter(delete_time=None,order_id=projectPay.order_id)
            mfobj = FactoryMake.objects.filter(delete_time=None,order_id=projectPay.order_id)
            order_sn = ""
            coop_mode = ""
            ticketing_custom = ""
            for one in planOrder:
                order_sn = order_sn + one.order_sn +"|"
            for one1 in mfobj:
                coop_mode  = coop_mode + one1.coop_mode + "|"
                ticketing_custom = ticketing_custom + one1.ticketing_custom + "|"
            # 结算列表信息
            if projectPay.type == 1:
                samp = getMakePayInfo1(nid)
            if projectPay.type == 2:
                samp = getMakePayInfo2(nid)
            if projectPay.type == 3:
                samp = getMakePayInfo3(nid)

            temp = {}
            temp["order_sn"] = order_sn
            temp["coop_mode"] = coop_mode
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp['work_type'] = order.work_type
            temp["custom"] = projectPay.custom
            temp["pay_custom"] = projectPay.pay_custom
            temp["pay_amount"] = projectPay.pay_amount
            temp["finish_amount"] = projectPay.finish_amount
            temp['order_id'] =projectPay.order_id
            temp['type'] = projectPay.type
            temp["data"] = samp
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的报价项目"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 批量删除 生产组织其他应付

    @csrf_exempt
    def delete(self, request):
        sn = "5020201,5020202"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = ProductPayInfo.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "生产应付付款操作成功删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "生产应付付款操作不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class sampleAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                rObj = PlanOrder.objects.filter(delete_time=None)
                if status == 0:
                    rObj = rObj.filter(~Q(sure_status=1))
                if status ==1:
                    rObj = rObj.filter(sure_status=1)
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if brand:
                    rObj = rObj.filter(brand=brand)

                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["brand"] = one.brand
                    zamp["goods_name"] = one.goods_name
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    orderline = OrderClothShip.objects.filter(order_id=one.id)
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_pay == 1:
                            c_pay_sure_num += 1
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    otherPay = FactoryMake.objects.filter(order_id=one.id)
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_pay == 1:
                            other_pay_sure_num +=1
                    zamp["make_pay_num"] = other_pay_num
                    zamp["make_pay_sure_num"] = other_pay_sure_num
                    zamp["status"] = status
                    samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

##############################################################成衣应付-其他
class sampleOtherAccountsView(APIView):
    # 添加/编辑 生产组织其他应付
    @csrf_exempt
    def post(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data  = request.data
        try:
            order_id = data['order_id']
        except:
            msg = "请输入订单id"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        dataone =data['data']
        for done in dataone:
            d_num = d_num + 1
            valObjline = sampOtherAcountOneSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid =done['id']
                    if mid:
                        bObj = SamplePayStatic.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = SamplePayStatic()
                        bObj.create_time = dt
                    bObj.order_id = data['order_id']
                    bObj.custom = done['custom']
                    bObj.pay_custom = done['pay_custom']
                    bObj.pay_comment = done['pay_comment']
                    bObj.price_type = done['price_type']
                    bObj.pay_num = done['pay_num']
                    bObj.pay_price = done['pay_price']
                    bObj.pay_amount = done['pay_amount']
                    bObj.finish_amount = Decimal(0)
                    bObj.is_sure = 1
                    bObj.is_finish_pay = 0
                    bObj.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑其他应收款"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 生产组织其他应付
    @csrf_exempt
    def delete(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = SamplePayStatic.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "生产组织其他应付删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "生产组织其他应付不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class sampleOtherAccountsOneView(APIView):
    # 获取生产组织其他应付
    @csrf_exempt
    def get(self, request, nid):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            samplePay = SamplePayStatic.objects.filter(delete_time = None,order_id = nid)
            custom_dic, custom_list = getAllCustom(nid)
            orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
            planOrder = PlanOrderLine.objects.filter(order_id=nid)
            order_sn = ""
            for one in planOrder:
                order_sn = order_sn + one.order_sn + "|"
            fmObj = FactoryMake.objects.filter(order_id=nid)
            coop_mode = ''
            ticketing_custom = ''
            for o in fmObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            temp = {}
            temp["data"] = samplePay.values()
            temp['order_type'] =order.order_type
            temp['provide'] = "南通风尚国际"
            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = orderObj.dhkhao
            temp["price_code"] = orderObj.price_code
            temp["work_type"] = orderObj.work_type
            temp['custom_list'] = custom_list
            temp['custom_dic'] = custom_dic
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "确认生产组织其他应付"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

#########################################成衣应付-计算工具
class sampleAccountsToolsView(APIView):
    # 添加/编辑 计算工具
    @csrf_exempt
    def post(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data = request.data
        dataone =data
        for done in dataone:
            d_num = d_num + 1
            valObjline = samptoolsOneSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid =done['id']
                    if mid:
                        bObj = SampTools.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = SampTools()
                        bObj.create_time = dt
                    bObj.tools_name = done['tools_name']
                    bObj.price_type = done['price_type']
                    bObj.fee_lv_1 = done['fee_lv_1']
                    bObj.fee_lv_2 = done['fee_lv_2']
                    bObj.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑计算工具"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 生产组织其他应付
    @csrf_exempt
    def delete(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = SampTools.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "计算工具删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "计算工具不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class sampleAccountsToolsOneView(APIView):
    # 获取生产组织其他应付
    @csrf_exempt
    def get(self, request, nid):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            toolsObj = SampTools.objects.filter(delete_time=None)
            temp = {}
            temp["data"] = toolsObj.values()
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "获取数据失败！"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class samplePayNumAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                rObj = PlanOrder.objects.filter(delete_time=None)
                if status == 0:
                    rObj = rObj.filter(~Q(sure_status=1))
                if status ==1:
                    rObj = rObj.filter(sure_status=1)
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if brand:
                    rObj = rObj.filter(brand=brand)

                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["brand"] = one.brand
                    zamp["goods_name"] = one.goods_name
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    orderline = PlanOrderLine.objects.filter(order_id=one.id)
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_price ==1:
                            c_pay_sure_num +=1
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    otherPay = OrderPay.objects.filter(order_id=one.id)
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_price == 1:
                            other_pay_sure_num +=1
                    zamp["other_pay_num"] = other_pay_num
                    zamp["other_pay_sure_num"] = other_pay_sure_num
                    zamp["status"] = status
                    samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class samplePayNumAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            order = PlanOrder.objects.get(id=nid)
            planPrice = PlanPrice.objects.get(plan_id =order.plan_id)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            factoryObj = FactoryMake.objects.filter(order_id=nid)
            order_sn = ""
            for o1 in orderLine:
                order_sn = order_sn + o1.order_sn + "|"

            coop_mode = ''
            ticketing_custom = ''
            for o in factoryObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            coop_mode_all = ""
            # 检品数据
            fm_list = []
            for one in factoryObj:
                fm_dic = {}
                fm_dic['make_factory_id'] = one.id
                fm_dic['make_factory'] = one.make_factory
                fm_dic['coop_mode'] = one.coop_mode
                coop_mode_all =coop_mode_all +one.coop_mode + "|"
                fm_dic['ticketing_custom'] = one.ticketing_custom
                order_line_list = []
                # 订单项数据
                for one1 in orderLine:
                    jamp  = {}
                    samp,zemp = getOrderFactoryInfoColor(nid,one1.id,one.id)
                    jamp['order_line_one'] = zemp
                    jamp['order_custom'] = one1.order_custom
                    jamp['order_type'] = one1.order_custom
                    sampPayfee = SampPayFeeInfo.objects.filter(factory_make_id=one.id,order_line_id=one1.id)
                    if sampPayfee.count()>0:
                        jamp['price_type'] = sampPayfee[0].price_type
                        jamp['pay_amount'] = sampPayfee[0].pay_amount
                        jamp['custom'] = one.coop_mode
                        jamp['pay_custom'] = "南通风尚国际"
                    else:
                        jamp['price_type'] = "人民币"
                        jamp['pay_amount'] = None
                        jamp['custom'] = one.coop_mode
                        jamp['pay_custom'] = "南通风尚国际"
                    order_line_list.append(zemp)
                fm_dic['order_line_info'] = order_line_list
                fm_list.append(fm_dic)
            temp = {}
            temp["data"] = fm_list
            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp["work_type"] = order.work_type
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应加工费报价"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def post(self, request, nid):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        valObj = sampleMakeAccountOneSerializer(data=request.data)
        data = request.data
        if valObj.is_valid():
            try:
                dt = datetime.now()
                mid = data['id']
                if mid:
                    bObj = SampPayFeeInfo.objects.get(id=mid)
                    bObj.update_time = dt
                else:
                    cObj = SampPayFeeInfo.objects.filter(factory_make_id=nid,order_line_id=data['order_line_id'])
                    if cObj.count()>0:
                        bObj = cObj[0]
                        bObj.update_time = dt
                    else:
                        bObj = SampPayFeeInfo()
                        bObj.create_time = dt
                bObj.price_type = data["price_type"]
                bObj.order_line_id = data["order_line_id"]
                bObj.custom = data["custom"]
                bObj.pay_custom = data["pay_custom"]
                bObj.pay_comment = data["pay_comment"]
                try:
                    bObj.samp_id = data["samp_id"]
                except:
                    pass
                bObj.pay_amount = data["pay_amount"]
                bObj.factory_make_id =nid
                bObj.pay_project ="成衣结算"
                bObj.is_sure = 1
                bObj.pay_num = 1
                bObj.save()
                msg = "成衣结算数量和报价"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "id参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

######################################成衣应付---应付账目

class sampleInAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderInAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                search_time_type = valObj.data['search_time_type'] if valObj.data['search_time_type'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else ""
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else ""
                invoice_num = valObj.data['invoice_num'] if valObj.data['invoice_num'] is not None else ""
                fee_num = valObj.data['fee_num'] if valObj.data['fee_num'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if search_time_type == 1:
                    if start_time:
                        rObj = rObj.filter(create_time__gte=start_time)
                    if end_time:
                        rObj = rObj.filter(create_time__lte=end_time)
                if search_time_type == 2:
                    if start_time:
                        rObj = rObj.filter(indicate_time__gte = start_time)
                    if end_time:
                        rObj = rObj.filter(indicate_time__lte = end_time)
                if invoice_num:
                    rObj = rObj.filter(invoice_num=invoice_num)
                if fee_num:
                    rObj = rObj.filter(custom=fee_num)
                if status:
                    rObj = rObj.filter(pay_status=status)
                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["invoice_num"] = one.invoice_num
                    zamp["fee_num"] = one.fee_num
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    facObj = FactoryMake.objects.filter(order_id = one.id)
                    orderLine = PlanOrderLine.objects.filter(order_id=one.id)
                    c_pay_num = 0
                    c_pay_sure_num = 0
                    all_amount = Decimal(0)
                    pay_amount = Decimal(0)
                    for o1 in facObj:
                        for o2 in orderLine:
                            sampfeeObj = SampPayFeeInfo.objects.filter(order_line_id=o2.id,factory_make_id=o1.id)
                            if sampfeeObj.count()>0:
                                c_pay_num +=1
                                if sampfeeObj[0].is_sure == 1:
                                    c_pay_sure_num += 1
                                    if sampfeeObj[0].pay_amount:
                                        all_amount += sampfeeObj[0].pay_amount
                                    if sampfeeObj[0].finish_amount:
                                        pay_amount += sampfeeObj[0].finish_amount
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    samplesta = SamplePayStatic.objects.filter(order_id=one.id)
                    other_pay_num = samplesta.count()
                    other_pay_sure_num = 0
                    for o2 in samplesta:
                        if o2.is_sure == 1:
                            other_pay_sure_num += 1
                            if o2.pay_amount:
                                all_amount += o2.pay_amount
                            if o2.finish_amount:
                                pay_amount += o2.finish_amount
                    zamp["other_pay_num"] = other_pay_num
                    zamp["other_pay_sure_num"] = other_pay_sure_num
                    try:
                        zamp["pay_finish_deg"] = pay_amount/all_amount
                    except:
                        zamp["pay_finish_deg"] = 0

                    zamp["all_amount"] = all_amount
                    zamp["pay_amount"] = pay_amount
                    zamp["status"] = "订单状态"
                    samp.append(zamp)
                temp = {}
                pay_info = getOrderPayNum()
                temp["data"] = samp
                temp['order_pay_info'] = pay_info
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 新增订单收款结算
    @csrf_exempt
    def post(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data  = request.data
        try:
            order_id = data['order_id']
        except:
            msg = "请输入订单id"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        dataone =data['data']
        for done in dataone:
            d_num = d_num + 1
            valObjline = sampInaccountSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############成衣样品应付#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid = done['id']
                    if mid:
                        bObj = SamplePayInfoList.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = SamplePayInfoList()
                        bObj.create_time = dt
                    bObj.pay_time = done['pay_time']
                    bObj.order_id = data['order_id']
                    bObj.custom = done['custom']
                    bObj.pay_custom = done['pay_custom']
                    bObj.price_type = done['price_type']
                    bObj.pay_amount = done['pay_amount']
                    bObj.pay_mode = done['pay_mode']
                    bObj.pay_y_amount = done['pay_y_amount']
                    bObj.pay_n_amount_one = done['pay_n_amount_one']
                    bObj.beizhun = done['beizhun']
                    bObj.samp_info_id = done['samp_info_id']
                    bObj.sample_static_id = done['sample_static_id']
                    bObj.save()
                    #更改账目状态
                    try:
                        if not mid:
                            if done['account_type'] == 1:
                                sampInfoObj = SampPayFeeInfo.objects.get(id=done['samp_info_id'])
                                if sampInfoObj.finish_amount:
                                    sampInfoObj.finish_amount +=  done['pay_amount']
                                else:
                                    sampInfoObj.finish_amount = done['pay_amount']
                                if sampInfoObj.finish_amount==sampInfoObj.pay_amount:
                                    sampInfoObj.is_finish = 1
                                sampInfoObj.save()

                            if done['account_type'] == 2:
                                sampStaObj = SamplePayStatic.objects.get(id=done['sample_static_id'])
                                if sampStaObj.finish_amount:
                                    sampStaObj.finish_amount += done['pay_amount']
                                else:
                                    sampStaObj.finish_amount = done['pay_amount']
                                if sampStaObj.finish_amount == sampStaObj.pay_amount:
                                    sampStaObj.is_finish_pay = 1
                                sampStaObj.save()
                    except:
                        pass

                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "保存收款结算信息"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #批量删除 发货方案
    @csrf_exempt
    def delete(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = SamplePayInfoList.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "收款结算删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "收款结算不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class sampleInAccountsOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            data = request.query_params
            try:
                account_type = int(data['account_type'])
                samp_info_id = int(data['samp_info_id'])
                sample_static_id = int(data['sample_static_id'])
            except:
                account_type = 0
                samp_info_id = 0
                sample_static_id = 0
            order = PlanOrder.objects.get(id=nid)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)

            z_renminbi = {}
            z_meiyuan = {}
            z_ouyuan = {}
            z_renminbi_data = []
            z_meiyuan_data = []
            z_ouyuan_data = []
            z_renminbi_amount =Decimal(0)
            z_meiyuan_amount = Decimal(0)
            z_ouyuan_amount = Decimal(0)
            z_renminbi_amount_finish = Decimal(0)
            z_meiyuan_amount_finish = Decimal(0)
            z_ouyuan_amount_finish = Decimal(0)

            # 成衣结算
            order_sn = ""
            if account_type==0 or account_type==1:
                for o1 in orderLine:
                    order_sn = order_sn + o1.order_sn + "|"
                    if account_type==1 and samp_info_id:
                        sampInfoObj = SampPayFeeInfo.objects.filter(order_line_id=o1.id).order_by("price_type")
                    else:
                        sampInfoObj = SampPayFeeInfo.objects.filter(order_line_id=o1.id,id=samp_info_id).order_by("price_type")
                    for o2 in sampInfoObj:
                        samp = {}
                        samp['price_type'] = o2.price_type
                        samp['reciep_custom'] = o2.custom
                        samp['pay_custom'] = o2.pay_custom
                        samp['pay_amount'] = o2.pay_amount
                        samp['finish_amount'] = o2.finish_amount
                        samp['order_id'] = nid
                        samp['account_type'] = 1
                        samp['samp_info_id'] = o2.id
                        samp['sample_static_id'] = 0
                        if o2.price_type == "人民币":
                            z_renminbi_data.append(samp)
                            z_renminbi_amount +=o2.pay_amount
                            if o2.finish_amount:
                                z_renminbi_amount_finish += o2.finish_amount
                        if o2.price_type == "美元":
                            z_meiyuan_data.append(samp)
                            z_meiyuan_amount += o2.pay_amount
                            if o2.finish_amount:
                                z_meiyuan_amount_finish += o2.finish_amount
                        if o2.price_type == "欧元":
                            z_ouyuan_data.append(samp)
                            z_ouyuan_amount += o2.pay_amount
                            if o2.finish_amount:
                                z_ouyuan_amount_finish += o2.finish_amount
            if account_type == 0 or account_type == 2:
                if account_type == 2 and sample_static_id:
                    sampPayStatic = SamplePayStatic.objects.filter(order_id=nid,id=sample_static_id)
                else:
                    sampPayStatic = SamplePayStatic.objects.filter(order_id=nid)
                for o3 in sampPayStatic:
                    samp = {}
                    samp['price_type'] = o3.price_type
                    samp['reciep_custom'] = o3.custom
                    samp['pay_custom'] = o3.pay_custom
                    samp['pay_amount'] = o3.pay_amount
                    samp['finish_amount'] = o3.finish_amount
                    samp['order_id'] = nid
                    samp['account_type'] = 2
                    samp['samp_info_id'] = 0
                    samp['sample_static_id'] = o3.id
                    if o3.price_type == "人民币":
                        z_renminbi_data.append(samp)
                        z_renminbi_amount += o3.pay_amount
                        if o3.finish_amount:
                            z_renminbi_amount_finish += o3.finish_amount
                    if o3.price_type == "美元":
                        z_meiyuan_data.append(samp)
                        z_meiyuan_amount += o3.pay_amount
                        if o3.finish_amount:
                            z_renminbi_amount_finish += o3.finish_amount
                    if o3.price_type == "欧元":
                        z_ouyuan_data.append(samp)
                        z_ouyuan_amount += o3.pay_amount
                        if o3.finish_amount:
                            z_renminbi_amount_finish += o3.finish_amount

            # 统计信息
            z_renminbi['price_type'] = "人民币"
            z_renminbi['all_pay_amount'] =z_renminbi_amount
            z_renminbi['all_no_amount'] = z_renminbi_amount - z_renminbi_amount_finish
            z_renminbi['data'] = z_renminbi_data

            z_meiyuan['price_type'] = "美元"
            z_meiyuan['all_pay_amount'] = z_meiyuan_amount
            z_meiyuan['all_no_amount'] = z_meiyuan_amount - z_renminbi_amount_finish
            z_meiyuan['data'] = z_meiyuan_data

            z_ouyuan['price_type'] = "欧元"
            z_ouyuan['all_pay_amount'] = z_ouyuan_amount
            z_ouyuan['all_no_amount'] = z_ouyuan_amount - z_renminbi_amount_finish
            z_ouyuan['data'] = z_ouyuan_data

            # 结算列表信息
            if account_type == 2 and sample_static_id:
                sampPayInfoList = SamplePayInfoList.objects.filter(delete_time=None,order_id = nid,sample_static_id=sample_static_id)
            elif account_type == 1 and samp_info_id:
                sampPayInfoList = SamplePayInfoList.objects.filter(delete_time=None, order_id=nid,samp_info_id=samp_info_id)
            else:
                sampPayInfoList = SamplePayInfoList.objects.filter(delete_time=None, order_id=nid)
            temp = {}
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp["data"] = sampPayInfoList.values()
            temp["payData"] = {
                "renminbi":z_renminbi,
                "meiyuan":z_meiyuan,
                "ouyuan":z_ouyuan
            }
            temp['order_id'] =nid
            custom_dic, custom_list = getAllCustom(nid)
            temp["custom_dic"] = custom_dic
            temp['custom_list'] = custom_list
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的成衣样品的应付"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def put(self, request, nid):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        try:
            dt = datetime.now()
            # 订单项
            order = PlanOrder.objects.get(id=nid)
            orderLine = PlanOrderLine.objects.filter(order_id = nid)
            for one in orderLine:
               sampInfoObj = SampPayFeeInfo.objects.filter(order_line_id=one.id)
               for o1 in sampInfoObj:
                    o1.is_finish = 1
                    o1.finish_amount = o1.pay_amount
                    o1.save()
            sampStaObj = SamplePayStatic.objects.filter(order_id=nid)
            for o2 in sampStaObj:
                o2.is_finish_pay = 1
                o2.finish_amount = o2.pay_amount
                o2.save()
            msg = "确认全部收款完成"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "id参数错误"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class sampleInAllAccountsView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = orderInAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                search_time_type = valObj.data['search_time_type'] if valObj.data['search_time_type'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else ""
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else ""
                invoice_num = valObj.data['invoice_num'] if valObj.data['invoice_num'] is not None else ""
                fee_num = valObj.data['fee_num'] if valObj.data['fee_num'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if search_time_type == 1:
                    if start_time:
                        rObj = rObj.filter(create_time__gte=start_time)
                    if end_time:
                        rObj = rObj.filter(create_time__lte=end_time)
                if search_time_type == 2:
                    if start_time:
                        rObj = rObj.filter(indicate_time__gte = start_time)
                    if end_time:
                        rObj = rObj.filter(indicate_time__lte = end_time)
                if invoice_num:
                    rObj = rObj.filter(invoice_num=invoice_num)
                if fee_num:
                    rObj = rObj.filter(custom=fee_num)
                if status:
                    rObj = rObj.filter(pay_status=status)
                samp = []
                for one in rObj:
                    # 是否确认
                    facObj = FactoryMake.objects.filter(order_id = one.id)
                    orderLine = PlanOrderLine.objects.filter(order_id=one.id)
                    c_pay_num = 0
                    c_pay_sure_num = 0
                    all_amount = Decimal(0)
                    pay_amount = Decimal(0)
                    for o1 in facObj:
                        for o2 in orderLine:
                            sampfeeObj = SampPayFeeInfo.objects.filter(order_line_id=o2.id,factory_make_id=o1.id)
                            if sampfeeObj.count()>0:
                                zamp = {}
                                zamp["order_id"] = one.id
                                zamp["create_time"] = one.create_time
                                zamp["indicate_time"] = one.indicate_time
                                zamp["order_type"] = one.order_type
                                zamp["custom"] = one.custom
                                zamp["price_code"] = one.price_code
                                zamp["dhkhao"] = one.dhkhao
                                zamp["invoice_num"] = one.invoice_num
                                zamp["fee_num"] = one.fee_num
                                zamp["order_num"] = one.order_num

                                zamp["receip_custom"] = sampfeeObj[0].custom
                                zamp["pay_custom"] =sampfeeObj[0].pay_custom
                                zamp["price_type"] = sampfeeObj[0].price_type
                                zamp["pay_amount"] = sampfeeObj[0].pay_amount
                                try:
                                    zamp['pay_finish_deg'] = round(sampfeeObj[0].finish_amount/ sampfeeObj[0].pay_amount, 2)
                                except:
                                    zamp['pay_finish_deg'] = 0
                                zamp['is_finish'] = sampfeeObj[0].is_finish
                                zamp['fee_no_status'] = sampfeeObj[0].fee_no_status
                                zamp["account_type"] = 1
                                zamp["samp_pay_fee_info_id"] = sampfeeObj[0].id
                                zamp["sample_pay_static_id"] = 0
                                zamp["status"] = "订单状态"
                                samp.append(zamp)
                    samplesta = SamplePayStatic.objects.filter(order_id=one.id)

                    for o2 in samplesta:
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num

                        zamp["receip_custom"] = o2.custom
                        zamp["pay_custom"] = o2.pay_custom
                        zamp["price_type"] = o2.price_type
                        zamp["pay_amount"] = o2.pay_amount
                        try:
                            zamp['pay_finish_deg'] = round(o2.finish_amount / o2.pay_amount, 2)
                        except:
                            zamp['pay_finish_deg'] = 0
                        zamp['is_finish'] = o2.is_finish_pay
                        zamp['fee_no_status'] = o2.fee_no_status
                        zamp["account_type"] = 1
                        zamp["samp_pay_fee_info_id"] = 0
                        zamp["sample_pay_static_id"] = o2.id
                        zamp["status"] = "订单状态"
                        samp.append(zamp)
                temp = {}
                pay_info = getOrderPayNum()
                temp["data"] = samp
                temp['order_pay_info'] = pay_info
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



##############################################

# 未完成开票/已完成开票
class showReceiptView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        sn = "60101,60102"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = showReceiptSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if sort_type == 1:
                    rObj = rObj.order_by("indicate_time")
                if sort_type == 2:
                    rObj = rObj.order_by("create_time")
                samp = []

                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["invoice_num"] = one.invoice_num
                    zamp["fee_num"] = one.fee_num
                    zamp["order_num"] = one.order_num
                    zamp["status"] = "订单状态"
                    samp.append(zamp)

                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

# 采购发票档案
class showReceiptBuyDataView(APIView):
    @csrf_exempt
    def get(self, request):
        sn = "60104"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = showReceiptDataSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                receip_custom = valObj.data['receip_custom'] if valObj.data['receip_custom'] is not None else ""
                pay_custom = valObj.data['pay_custom'] if valObj.data['pay_custom'] is not None else ""
                fee_no_status = valObj.data['fee_no_status'] if valObj.data['fee_no_status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if sort_type == 1:
                    rObj = rObj.order_by("indicate_time")
                if sort_type == 2:
                    rObj = rObj.order_by("create_time")
                samp = []

                for one in rObj:
                    prodObj = ProductPayStatic.objects.filter(~Q(order_cloth_ship_id=0),delete_time=None,order_id=one.id)
                    if receip_custom:
                        prodObj = prodObj.filter(custom=receip_custom)
                    if pay_custom:
                        prodObj = prodObj.filter(pay_custom=pay_custom)
                    if fee_no_status:
                        prodObj = prodObj.filter(fee_no_status=fee_no_status)
                    for o1 in prodObj:
                        orderClothObj = OrderClothShip.objects.get(id=o1.order_cloth_ship_id)
                        planMObj = PlanMaterial.objects.get(id=orderClothObj.plan_material_id)
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        zamp["status"] = "订单状态"
                        zamp['cloth_name'] = orderClothObj.cloth_name
                        zamp['m_unit'] = planMObj.m_unit
                        zamp['provide_time'] = orderClothObj.update_time
                        zamp['send_num'] = orderClothObj.buy_all_num

                        zamp['pay_price'] = o1.pay_price
                        zamp['pay_amount'] = o1.pay_amount
                        zamp['receip_custom'] = o1.custom
                        zamp['pay_custom'] = o1.pay_custom
                        zamp['fee_no'] = o1.fee_no
                        zamp['fee_amount'] = o1.fee_amount
                        zamp['fee_no_status'] = o1.fee_no_status
                        samp.append(zamp)

                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


# 加工发票档案
class showReceiptMakeDataView(APIView):
    @csrf_exempt
    def get(self, request):
        sn = "60104"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = showReceiptDataSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                receip_custom = valObj.data['receip_custom'] if valObj.data['receip_custom'] is not None else ""
                pay_custom = valObj.data['pay_custom'] if valObj.data['pay_custom'] is not None else ""
                fee_no_status = valObj.data['fee_no_status'] if valObj.data['fee_no_status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if sort_type == 1:
                    rObj = rObj.order_by("indicate_time")
                if sort_type == 2:
                    rObj = rObj.order_by("create_time")
                samp = []

                for one in rObj:
                    prodObj = ProductPayStatic.objects.filter(~Q(factory_make_id=0),delete_time=None,order_id=one.id)
                    if receip_custom:
                        prodObj = prodObj.filter(custom=receip_custom)
                    if pay_custom:
                        prodObj = prodObj.filter(pay_custom=pay_custom)
                    if fee_no_status:
                        prodObj = prodObj.filter(fee_no_status=fee_no_status)
                    for o1 in prodObj:
                        fmObj = FactoryMake.objects.get(id=o1.factory_make_id)
                        fmlObj = FactoryMakeLine.objects.filter(factory_make_id=o1.factory_make_id)
                        inspect_num = 0
                        b_num = 0
                        goods_num = 0
                        make_num = 0
                        recover_b_num = 0
                        for o2 in fmlObj:
                            if o2.inspect_num:
                                inspect_num += o2.inspect_num
                            if o2.b_num:
                                b_num +=o2.b_num
                            if o2.make_num:
                                make_num +=o2.make_num
                            if o2.recover_b_num:
                                recover_b_num +=o2.recover_b_num
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        zamp["status"] = "订单状态"
                        zamp['goods_num'] = inspect_num-b_num
                        zamp['b_num'] = b_num
                        zamp['b_amount'] = round(Decimal(b_num / inspect_num) * o1.pay_amount,2)
                        zamp['goods_amount'] = round(Decimal((inspect_num-b_num) / inspect_num) * o1.pay_amount,2)

                        zamp['price_type'] = o1.price_type
                        zamp['pay_price'] = o1.pay_price
                        zamp['pay_amount'] = o1.pay_amount
                        zamp['receip_custom'] = o1.custom
                        zamp['pay_custom'] = o1.pay_custom
                        zamp['fee_no'] = o1.fee_no
                        zamp['fee_amount'] = o1.fee_amount
                        zamp['fee_no_status'] = o1.fee_no_status
                        samp.append(zamp)

                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



# 成衣档案
class showReceiptSampDataView(APIView):
    @csrf_exempt
    def get(self, request):
        sn = "60104"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = showReceiptDataSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                receip_custom = valObj.data['receip_custom'] if valObj.data['receip_custom'] is not None else ""
                pay_custom = valObj.data['pay_custom'] if valObj.data['pay_custom'] is not None else ""
                fee_no_status = valObj.data['fee_no_status'] if valObj.data['fee_no_status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if sort_type == 1:
                    rObj = rObj.order_by("indicate_time")
                if sort_type == 2:
                    rObj = rObj.order_by("create_time")
                samp = []

                for one in rObj:
                    orderLine = PlanOrderLine.objects.filter(order_id=one.id)
                    for o1 in orderLine:

                        sampObj = SampPayFeeInfo.objects.filter(order_line_id=o1.id)
                        if receip_custom:
                            sampObj = sampObj.filter(custom=receip_custom)
                        if pay_custom:
                            sampObj = sampObj.filter(pay_custom=pay_custom)
                        if fee_no_status:
                            sampObj = sampObj.filter(fee_no_status=fee_no_status)
                        for o3 in sampObj:
                            zamp = {}
                            zamp["order_id"] = one.id
                            zamp["create_time"] = one.create_time
                            zamp["indicate_time"] = one.indicate_time
                            zamp["order_type"] = one.order_type
                            zamp["custom"] = one.custom
                            zamp["price_code"] = one.price_code
                            zamp["dhkhao"] = one.dhkhao
                            zamp["invoice_num"] = one.invoice_num
                            zamp["fee_num"] = one.fee_num
                            zamp["order_num"] = one.order_num
                            zamp["status"] = "订单状态"
                            zamp['pay_project'] = o3.pay_project
                            zamp['price_type'] = o3.price_type
                            zamp['pay_price'] = o3.pay_amount
                            zamp['pay_amount'] = o3.pay_amount
                            zamp['receip_custom'] = o3.custom
                            zamp['pay_custom'] = o3.pay_custom
                            zamp['fee_no'] = o3.fee_no
                            zamp['fee_amount'] = o3.fee_amount
                            zamp['fee_no_status'] = o3.fee_no_status
                            samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



# 其他发票档案
class showReceiptOtherDataView(APIView):
    @csrf_exempt
    def get(self, request):
        sn = "60104"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = showReceiptDataSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                receip_custom = valObj.data['receip_custom'] if valObj.data['receip_custom'] is not None else ""
                pay_custom = valObj.data['pay_custom'] if valObj.data['pay_custom'] is not None else ""
                fee_no_status = valObj.data['fee_no_status'] if valObj.data['fee_no_status'] is not None else 0
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if sort_type == 1:
                    rObj = rObj.order_by("indicate_time")
                if sort_type == 2:
                    rObj = rObj.order_by("create_time")
                samp = []

                for one in rObj:
                    prodObj = ProductPayStatic.objects.filter(type=3,delete_time=None,order_id=one.id)
                    if receip_custom:
                        prodObj = prodObj.filter(custom=receip_custom)
                    if pay_custom:
                        prodObj = prodObj.filter(pay_custom=pay_custom)
                    if fee_no_status:
                        prodObj = prodObj.filter(fee_no_status=fee_no_status)
                    for o1 in prodObj:
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        zamp["status"] = "订单状态"
                        zamp['pay_project'] = o1.pay_project
                        zamp['price_type'] = o1.price_type
                        zamp['pay_price'] = o1.pay_price
                        zamp['pay_amount'] = o1.pay_amount
                        zamp['receip_custom'] = o1.custom
                        zamp['pay_custom'] = o1.pay_custom
                        zamp['fee_no'] = o1.fee_no
                        zamp['fee_amount'] = o1.fee_amount
                        zamp['fee_no_status'] = o1.fee_no_status
                        samp.append(zamp)
                    orderPay = OrderPay.objects.filter(order_id=one.id)
                    for o2 in orderPay:
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        zamp["status"] = "订单状态"
                        zamp['pay_project'] = o2.pay_content
                        zamp['price_type'] = o2.pay_type
                        zamp['pay_price'] = o2.pay_price
                        zamp['pay_amount'] = o2.amount
                        zamp['receip_custom'] = o2.custom
                        zamp['pay_custom'] = o2.provide_custom
                        zamp['fee_no'] = o2.fee_no
                        zamp['fee_amount'] = o2.fee_amount
                        zamp['fee_no_status'] = o2.fee_no_status
                        samp.append(zamp)
                    sampObj = SamplePayStatic.objects.filter(order_id=one.id)
                    for o3 in sampObj:
                        zamp = {}
                        zamp["order_id"] = one.id
                        zamp["create_time"] = one.create_time
                        zamp["indicate_time"] = one.indicate_time
                        zamp["order_type"] = one.order_type
                        zamp["custom"] = one.custom
                        zamp["price_code"] = one.price_code
                        zamp["dhkhao"] = one.dhkhao
                        zamp["invoice_num"] = one.invoice_num
                        zamp["fee_num"] = one.fee_num
                        zamp["order_num"] = one.order_num
                        zamp["status"] = "订单状态"
                        zamp['pay_project'] = o3.pay_comment
                        zamp['price_type'] = o3.price_type
                        zamp['pay_price'] = o3.pay_price
                        zamp['pay_amount'] = o3.pay_amount
                        zamp['receip_custom'] = o3.custom
                        zamp['pay_custom'] = o3.pay_custom
                        zamp['fee_no'] = o3.fee_no
                        zamp['fee_amount'] = o3.fee_amount
                        zamp['fee_no_status'] = o3.fee_no_status
                        samp.append(zamp)

                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



# 发票信息保存
class saveReceiptView(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = saveReceiptSerializer(data=request.data)
        if valObj.is_valid():
            try:
                if data["type"] == 3:
                    nid = data["fee_no_id"]
                    other_type = data["other_type"]
                    if other_type == 1:
                        bObj = OrderPay.objects.get(id=nid)
                        fee_no = ""
                        amount = ""
                        for one in data["fee_info"]:
                            fee_no += one["fee_no"] + "|"
                            amount += str(one["fee_amount"]) + "|"
                        bObj.fee_no = fee_no
                        bObj.fee_amount = amount
                        bObj.fee_no_status = 1
                        bObj.save()
                    if other_type == 2:
                        bObj = ProductPayStatic.objects.get(id=nid)
                        fee_no = ""
                        amount = ""
                        for one in data["fee_info"]:
                            fee_no += one["fee_no"] + "|"
                            amount += str(one["fee_amount"]) + "|"
                        bObj.fee_no = fee_no
                        bObj.fee_amount = amount
                        bObj.fee_no_status = 1
                        bObj.save()
                    if other_type == 3:
                        bObj = SamplePayStatic.objects.get(id=nid)
                        fee_no = ""
                        amount = ""
                        for one in data["fee_info"]:
                            fee_no += one["fee_no"] + "|"
                            amount += str(one["fee_amount"]) + "|"
                        bObj.fee_no = fee_no
                        bObj.fee_amount = amount
                        bObj.fee_no_status = 1
                        bObj.save()
                elif data['type'] == 4:
                    nid = data["fee_no_id"]
                    dt = datetime.now()
                    bObj = SampPayFeeInfo.objects.get(id=nid)
                    bObj.update_time = dt
                    fee_no = ""
                    amount = ""
                    for one in data["fee_info"]:
                        fee_no += one["fee_no"] + "|"
                        amount += str(one["fee_amount"]) + "|"
                    bObj.fee_no = fee_no
                    bObj.fee_amount = amount
                    bObj.fee_no_status = 1
                    bObj.save()

                else:
                    nid = data["fee_no_id"]
                    dt = datetime.now()
                    if nid:
                        bObj = FeeNo.objects.get(id=nid)
                        bObj.update_time = dt
                    else:
                        if data["type"] == 1:
                            cObj =FeeNo.objects.filter(order_cloth_ship_id = data["order_cloth_ship_id"])
                            if cObj.count()>0:
                                bObj = cObj[0]
                                bObj.update_time = dt
                            else:
                                bObj = FeeNo()
                                bObj.create_time = dt
                            bObj.order_cloth_ship_id = data["order_cloth_ship_id"]
                            bObj.order_line_id = 0
                            bObj.make_factory_id = 0
                            bObj.other_id = 0
                        elif data["type"] == 2:
                            cObj = FeeNo.objects.filter(make_factory_id=data["make_factory_id"])
                            if cObj.count() > 0:
                                bObj = cObj[0]
                                bObj.update_time = dt
                            else:
                                bObj = FeeNo()
                                bObj.create_time = dt
                            bObj.order_cloth_ship_id = 0
                            bObj.order_line_id = 0
                            bObj.make_factory_id = data["make_factory_id"]
                            bObj.other_id = 0
                        else:
                            bObj = FeeNo()
                            bObj.create_time = dt
                    bObj.type = data["type"]
                    bObj.order_id = data["order_id"]
                    fee_no = ""
                    amount = ""
                    for one in data["fee_info"]:
                        fee_no +=one["fee_no"] + "|"
                        amount +=str(one["fee_amount"]) + "|"
                    bObj.fee_no = fee_no
                    bObj.amount = amount
                    bObj.save()
                msg = "发票保存成功"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "id参数错误"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

# 获取采购发票

class getBuyReceiptOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        try:
            orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
            planOrder = PlanOrderLine.objects.filter(order_id=nid)
            order_sn = ""
            for one in planOrder:
                order_sn = order_sn + one.order_sn + "|"
            fmObj = FactoryMake.objects.filter(order_id=nid)
            coop_mode = ''
            ticketing_custom = ''
            fee_sure_num = 0
            for o in fmObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            orderClothShip = OrderClothShip.objects.filter(delete_time=None, order_id=nid).order_by(
                "order_cloth_id", "supplier")
            samplist = []
            supplier_list = []
            supplier_num = orderClothShip.count()
            supplier_sure_num = 0
            for one in orderClothShip:
                if one.is_sure_pay ==1:
                    supplier_sure_num +=1
                # 供应商
                supplier_list.append(one.supplier)
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
                samp['coop_mode'] = coop_mode
                samp['ticketing_custom'] = ticketing_custom
                if one.price_type:
                    samp['price_type'] = one.price_type
                else:
                    samp['price_type'] = "人民币"
                samp['all_amount'] = one.all_amount
                samp['is_inspect'] = one.is_inspect
                # 发票信息
                feeNo = FeeNo.objects.filter(order_cloth_ship_id=one.id)
                if feeNo.count()>0:
                    fee_no = feeNo[0].fee_no.split("|")
                    amount = feeNo[0].amount.split("|")
                    fee_no_y = []
                    amount_y = []
                    for l1 in fee_no:
                        if l1:
                            fee_no_y.append(l1)
                    for l2 in amount:
                        if l2:
                            amount_y.append(Decimal(l2))
                    samp['fee_no'] = fee_no_y
                    samp['fee_amount'] = amount_y
                    samp['fee_no_id'] = feeNo[0].id
                    samp['fee_no_status'] = "已完成"
                    fee_sure_num +=1
                else:
                    samp['fee_no'] = None
                    samp['fee_amount'] = None
                    samp['fee_no_id'] = 0
                    samp['fee_no_status'] = "未完成"
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
                samplist.append(samp)

            temp = {}
            supplier_no_num = supplier_num - supplier_sure_num
            temp["data"] = samplist
            temp['supplier_num'] = supplier_num
            temp['fee_sure_num'] = fee_sure_num
            temp['fee_no_num'] = supplier_num - fee_sure_num
            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = orderObj.dhkhao
            temp["price_code"] = orderObj.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = orderObj.invoice_num
            temp["fee_num"] = orderObj.fee_num
            temp["work_type"] = orderObj.work_type
            temp["supplier_list"] = list(set(supplier_list))
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的采购数据"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

# 获取加工费发票信息

class getMakeReceiptOneView(APIView):

    @csrf_exempt
    def get(self, request, nid):
        try:
            order = PlanOrder.objects.get(id=nid)
            planPrice = PlanPrice.objects.get(plan_id =order.plan_id)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            factoryObj = FactoryMake.objects.filter(order_id=nid)
            order_sn = ""
            for o1 in orderLine:
                order_sn = order_sn + o1.order_sn + "|"

            coop_mode = ''
            ticketing_custom = ''
            for o in factoryObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            coop_mode_all = ""
            # 检品数据
            fm_list = []
            for one in factoryObj:
                fm_dic = {}
                fm_dic['make_factory_id'] = one.id
                fm_dic['make_factory'] = one.make_factory
                fm_dic['coop_mode'] = one.coop_mode
                coop_mode_all =coop_mode_all +one.coop_mode + "|"
                fm_dic['ticketing_custom'] = one.ticketing_custom
                fm_dic['price_type'] = one.price_type
                fm_dic['plan_price'] = planPrice.plan_price
                fm_dic['amount'] = one.amount
                fm_dic['sure_amount'] = one.sure_amount

                # 发票信息
                feeNo = FeeNo.objects.filter(make_factory_id=one.id)
                if feeNo.count() > 0:
                    fee_no = feeNo[0].fee_no.split("|")
                    amount = feeNo[0].amount.split("|")
                    fee_no_y = []
                    amount_y = []
                    for l1 in fee_no:
                        if l1:
                            fee_no_y.append(l1)
                    for l2 in amount:
                        if l2:
                            amount_y.append(Decimal(l2))
                    fm_dic['fee_no'] = fee_no_y
                    fm_dic['fee_amount'] = amount_y
                    fm_dic['fee_no_id'] = feeNo[0].id
                    fm_dic['fee_no_status'] = "已完成"

                else:
                    fm_dic['fee_no'] = None
                    fm_dic['fee_amount'] = None
                    fm_dic['fee_no_id'] = 0
                    fm_dic['fee_no_status'] = "未完成"

                order_line_list = []
                # 订单项数据
                for one1 in orderLine:
                    jamp  = {}
                    samp,zemp = getOrderFactoryInfoColor(nid,one1.id,one.id)
                    jamp['order_line_one'] = zemp
                    jamp['custom'] = one1.order_custom
                    jamp['order_type'] = one1.order_custom
                    order_line_list.append(zemp)
                fm_dic['order_line_info'] = order_line_list
                fm_list.append(fm_dic)
            temp = {}
            temp["data"] = fm_list


            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp["work_type"] = order.work_type
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应加工费报价"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

# 获取其他发票信息
class getOtherReceiptOneView(APIView):

    @csrf_exempt
    def get(self, request, nid):
        try:
            order = PlanOrder.objects.get(id=nid)
            planPrice = PlanPrice.objects.get(plan_id =order.plan_id)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            factoryObj = FactoryMake.objects.filter(order_id=nid)
            order_sn = ""
            for o1 in orderLine:
                order_sn = order_sn + o1.order_sn + "|"

            coop_mode = ''
            ticketing_custom = ''
            for o in factoryObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            samp,other_num,other_fee_num = getOrderOtherFee(nid)
            temp = {}
            temp['data'] = samp
            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp['merchant']  = "南通风尚国际"
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp["work_type"] = order.work_type
            temp['other_num'] = other_num
            temp['other_fee_num'] = other_fee_num

            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应其他发票信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class getSampReceiptOneView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request, nid):
        try:
            order = PlanOrder.objects.get(id=nid)
            planPrice = PlanPrice.objects.get(plan_id =order.plan_id)
            orderLine = PlanOrderLine.objects.filter(order_id=nid)
            factoryObj = FactoryMake.objects.filter(order_id=nid)
            order_sn = ""
            for o1 in orderLine:
                order_sn = order_sn + o1.order_sn + "|"

            coop_mode = ''
            ticketing_custom = ''
            for o in factoryObj:
                coop_mode += o.coop_mode + '|'
                ticketing_custom += o.ticketing_custom + '|'
            coop_mode_all = ""
            # 检品数据
            fm_list = []
            for one in factoryObj:
                fm_dic = {}
                fm_dic['make_factory_id'] = one.id
                fm_dic['make_factory'] = one.make_factory
                fm_dic['coop_mode'] = one.coop_mode
                coop_mode_all =coop_mode_all +one.coop_mode + "|"
                fm_dic['ticketing_custom'] = one.ticketing_custom
                order_line_list = []
                # 订单项数据
                for one1 in orderLine:
                    jamp  = {}
                    samp,zemp = getOrderFactoryInfoColor(nid,one1.id,one.id)
                    jamp['order_line_one'] = zemp
                    jamp['order_custom'] = one1.order_custom
                    jamp['order_type'] = one1.order_type
                    sampPayfee = SampPayFeeInfo.objects.filter(factory_make_id=one.id,order_line_id=one1.id)
                    if sampPayfee.count()>0:
                        jamp['price_type'] = sampPayfee[0].price_type
                        jamp['pay_amount'] = sampPayfee[0].pay_amount
                        jamp['custom'] = one.coop_mode
                        jamp['pay_custom'] = "南通风尚国际"
                        jamp['fee_no'] = sampPayfee[0].fee_no
                        jamp['fee_amount'] = sampPayfee[0].fee_amount
                        jamp['file_url'] = sampPayfee[0].file_url
                        jamp['fee_no_status'] = sampPayfee[0].fee_no_status
                    else:
                        jamp['price_type'] = "人民币"
                        jamp['pay_amount'] = None
                        jamp['custom'] = one.coop_mode
                        jamp['pay_custom'] = "南通风尚国际"
                        jamp['fee_no'] = None
                        jamp['fee_amount'] = None
                        jamp['file_url'] = None
                        jamp['fee_no_status'] = None
                    order_line_list.append(jamp)
                fm_dic['order_line_info'] = order_line_list
                fm_list.append(fm_dic)
            temp = {}
            temp["data"] = fm_list
            temp['coop_mode'] = coop_mode
            temp['ticketing_custom'] = ticketing_custom
            temp['order_id'] = nid
            temp["dhkh"] = order.dhkhao
            temp["price_code"] = order.price_code
            temp["order_sn"] = order_sn
            temp["invoice_num"] = order.invoice_num
            temp["fee_num"] = order.fee_num
            temp["work_type"] = order.work_type
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应加工费报价"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


###################################结汇管理##############################

class showSurrenderView(APIView):
    # 获取结汇管理
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = orderAccountsLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                rObj = PlanOrder.objects.filter(delete_time=None)
                if status == 0:
                    rObj = rObj.filter(~Q(sure_status=1))
                if status ==1:
                    rObj = rObj.filter(sure_status=1)
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if brand:
                    rObj = rObj.filter(brand=brand)

                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["brand"] = one.brand
                    zamp["goods_name"] = one.goods_name
                    zamp["order_num"] = one.order_num
                    # 是否确认
                    orderline = OrderClothShip.objects.filter(order_id=one.id)
                    c_pay_num = orderline.count()
                    c_pay_sure_num = 0
                    for o1 in orderline:
                        if o1.is_sure_pay == 1:
                            c_pay_sure_num += 1
                    zamp["c_pay_num"] = c_pay_num
                    zamp["c_pay_sure_num"] = c_pay_sure_num
                    otherPay = FactoryMake.objects.filter(order_id=one.id)
                    other_pay_num = otherPay.count()
                    other_pay_sure_num = 0
                    for o2 in otherPay:
                        if o2.is_sure_pay == 1:
                            other_pay_sure_num +=1
                    zamp["make_pay_num"] = other_pay_num
                    zamp["make_pay_sure_num"] = other_pay_sure_num
                    zamp["status"] = status
                    samp.append(zamp)
                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 新增订单收款结算
    @csrf_exempt
    def post(self, request):
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        dataone =request.data
        for done in dataone:
            d_num = d_num + 1
            valObjline = showSurrenderSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid = done['id']
                    if mid:
                        bObj = OrderSurBp.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = OrderSurBp()
                        bObj.create_time = dt
                    bObj.order_id = done['order_id']
                    bObj.sur_lv = done['sur_lv']
                    bObj.sur_amount = done['sur_amount']
                    bObj.sur_bp = done['sur_bp']
                    bObj.bp_amount = done['bp_amount']
                    bObj.is_pay = 1
                    bObj.save()
                    # 订单是否全部确认
                    for o_id in done['order_id']:
                        planOrder = PlanOrder.objects.get(id=o_id)
                        planOrder.is_surrender = 1
                        planOrder.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "保存收款结算信息"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


###################################工资管理##############################

class showSalaryStandardView(APIView):
    # 获取工资标准
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = showStandSalaryOneSerializer(data=request.query_params)
        if valObj.is_valid():
            start, page_size, flag = zddpaginate(int(valObj.data['page']), int(valObj.data['page_size']))
            status = valObj.data['status'] if valObj.data['status'] is not None else 0
            department_id = valObj.data['department_id'] if valObj.data['department_id'] is not None else 0
            post_id = valObj.data['post_id'] if valObj.data['post_id'] is not None else 0
            name = valObj.data['name'] if valObj.data['name'] is not None else ""
            start_time = valObj.data['start'] if valObj.data['start'] is not None else ""
            end_time = valObj.data['end'] if valObj.data['end'] is not None else ""
            if not flag:
                msg = "访问页码错误，请确认"
                error_code = 10100
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            result = []
            try:
                dt = datetime.now()
                rObj = Archives.objects.filter(delete_time=None).order_by("job_number", "id")
                if department_id:
                    rObj = rObj.filter(department_id = department_id)
                if status:
                    rObj = rObj.filter(status = status)
                if post_id:
                    rObj = rObj.filter(post_id = post_id)
                if name:
                    rObj = rObj.filter(name = name)

                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start + page_size]
                    for o1 in rObj:
                        samp = {}
                        samp['id'] = o1.id
                        samp['job_number'] = o1.job_number
                        samp['name'] = o1.name
                        samp['gender'] = o1.gender
                        depObj = Department.objects.get(id=o1.department_id)
                        samp['department_name'] = depObj.department_name
                        postObj = Post.objects.get(id=o1.post_id)
                        samp['post_name'] = postObj.post_name
                        arcstand = ArchivesSalaryStandard.objects.filter(archives_id=o1.id)
                        if arcstand.count()>0:
                            samp['annual_salary'] = arcstand[0].annual_salary
                            samp['payment'] = arcstand[0].payment
                            samp['social_insurance_id'] = arcstand[0].social_insurance_id
                            samp['social_insurance_level'] = arcstand[0].social_insurance_level
                            samp['social_insurance_company'] = arcstand[0].social_insurance_company
                            samp['social_insurance_person'] = arcstand[0].social_insurance_person
                            samp['other_contributions_company'] = arcstand[0].other_contributions_company
                            samp['other_contributions_person'] = arcstand[0].other_contributions_person
                            samp['surplu_id'] = arcstand[0].surplu_id
                            samp['surplu_level'] = arcstand[0].surplu_level
                            samp['surplu_company'] = arcstand[0].surplu_company
                            samp['surplu_person'] = arcstand[0].surplu_person

                        else:
                            samp['annual_salary'] = None
                            samp['payment'] = None
                            samp['social_insurance_id'] = None
                            samp['social_insurance_level'] = None
                            samp['social_insurance_company'] = None
                            samp['social_insurance_person'] = None
                            samp['other_contributions_company'] = None
                            samp['other_contributions_person'] = None
                            samp['surplu_id'] = None
                            samp['surplu_level'] = None
                            samp['surplu_company'] = None
                            samp['surplu_person'] = None
                        samp["status"] = o1.status
                        result.append(samp)
                    temp = {}
                    temp["data"] = result
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = []
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
            except:
                msg = "未找到对应的工号"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 新增工资标准
    @csrf_exempt
    def post(self, request):
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        dataone =request.data
        for done in dataone:
            d_num = d_num + 1
            valObjline = showSalaryStandardSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid = done['id']
                    if mid:
                        bObj = ArchivesSalaryStandard.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        cObj = ArchivesSalaryStandard.objects.filter(archives_id=done['archives_id'])
                        if cObj.count()>0:
                            bObj = cObj[0]
                            bObj.update_time = dt
                        else:
                            bObj = ArchivesSalaryStandard()
                            bObj.create_time = dt
                    bObj.archives_id = done['archives_id']
                    bObj.annual_salary = done['annual_salary']
                    bObj.payment = done['payment']
                    bObj.social_insurance_id = done['social_insurance_id']
                    bObj.social_insurance_company = done['social_insurance_company']
                    bObj.social_insurance_person = done['social_insurance_person']
                    bObj.other_contributions_company = done['other_contributions_company']
                    bObj.other_contributions_person = done['other_contributions_person']
                    bObj.surplu_id = done['surplu_id']
                    bObj.surplu_company = done['surplu_company']
                    bObj.surplu_person = done['surplu_person']
                    bObj.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "保存员工工资标准"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class showMouthSalaryView(APIView):
    # 获取本月工资
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = showMouthSalaryOneSerializer(data=request.query_params)
        if valObj.is_valid():
            start, page_size, flag = zddpaginate(int(valObj.data['page']), int(valObj.data['page_size']))
            # status = valObj.data['status'] if valObj.data['status'] is not None else 0
            if not flag:
                msg = "访问页码错误，请确认"
                error_code = 10100
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            result = []
            try:
                dt = datetime.now()
                year = dt.year
                mouth = dt.month
                rObj = Archives.objects.filter(delete_time=None).order_by("job_number", "id")
                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start + page_size]
                    for o1 in rObj:
                        samp = {}
                        samp['id'] = o1.id
                        samp['job_number'] = o1.job_number
                        samp['name'] = o1.name
                        samp['gender'] = o1.gender
                        depObj = Department.objects.get(id=o1.department_id)
                        samp['department_name'] = depObj.department_name
                        postObj = Post.objects.get(id=o1.post_id)
                        samp['post_name'] = postObj.post_name
                        arcDetail = ArchivesSalaryDetail.objects.filter(archives_id=o1.id,year=year,mouth=mouth)
                        if arcDetail.count()>0:
                            samp['payment'] = arcDetail[0].payment
                            samp['social_insurance_person'] = arcDetail[0].social_insurance_person
                            samp['other_contributions_person'] = arcDetail[0].other_contributions_person
                            samp['surplu_person'] = arcDetail[0].surplu_person
                            samp['calculated_salary'] = arcDetail[0].calculated_salary
                            samp['other_salary'] = arcDetail[0].other_salary
                            samp['deduction'] = arcDetail[0].deduction
                            samp['comments'] = arcDetail[0].comments
                            samp['real_salary'] = arcDetail[0].real_salary
                        else:
                            arcstand = ArchivesSalaryStandard.objects.filter(archives_id=o1.id)
                            if arcstand.count()>0:
                                samp['payment'] = arcstand[0].payment
                                samp['social_insurance_person'] = arcstand[0].social_insurance_person
                                samp['other_contributions_person'] = arcstand[0].other_contributions_person
                                samp['surplu_person'] = arcstand[0].surplu_person
                                samp['calculated_salary'] = arcstand[0].payment - arcstand[0].social_insurance_person - arcstand[0].other_contributions_person - arcstand[0].surplu_person
                                samp['other_salary'] = None
                                samp['deduction'] = None
                                samp['comments'] = None
                                samp['real_salary'] = None
                            else:
                                samp['payment'] = None
                                samp['social_insurance_person'] = None
                                samp['other_contributions_person'] = None
                                samp['surplu_person'] = None
                                samp['calculated_salary'] = None
                                samp['other_salary'] = None
                                samp['deduction'] = None
                                samp['comments'] = None
                                samp['real_salary'] = None
                        result.append(samp)
                    arcDetail = ArchivesSalaryDetail.objects.filter(year=year, mouth=mouth).aggregate(nums=Sum('calculated_salary'))
                    temp = {}
                    temp["data"] = result
                    temp["year"] = year
                    temp["mouth"] = mouth
                    temp["worker_num"] = total
                    temp["salary_num"] = arcDetail['nums']
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = []
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
            except:
                msg = "未找到对应的工号"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 添加本月工资
    @csrf_exempt
    def post(self, request):
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        dataone =request.data
        for done in dataone:
            d_num = d_num + 1
            valObjline = showMouthSalarySerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid = done['id']
                    if mid:
                        bObj = ArchivesSalaryDetail.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        cObj = ArchivesSalaryDetail.objects.filter(archives_id=done['archives_id'],year=done['year'],mouth=done['mouth'])
                        if cObj.count()>0:
                            bObj = cObj[0]
                            bObj.update_time = dt
                        else:
                            bObj = ArchivesSalaryDetail()
                            bObj.create_time = dt
                    bObj.archives_id = done['archives_id']
                    bObj.year = done['year']
                    bObj.mouth = done['mouth']
                    bObj.payment = done['payment']
                    bObj.social_insurance_person = done['social_insurance_person']
                    bObj.other_contributions_person = done['other_contributions_person']
                    bObj.surplu_person = done['surplu_person']
                    bObj.calculated_salary = done['calculated_salary']
                    bObj.other_salary = done['other_salary']
                    bObj.deduction = done['deduction']
                    bObj.comments = done['comments']
                    bObj.real_salary = done['real_salary']
                    bObj.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "保存员工本月工资"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class showSalaryInfoView(APIView):
    # 获取工资档案
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = showStandSalaryOneSerializer(data=request.query_params)
        if valObj.is_valid():
            start, page_size, flag = zddpaginate(int(valObj.data['page']), int(valObj.data['page_size']))
            status = valObj.data['status'] if valObj.data['status'] is not None else 0
            department_id = valObj.data['department_id'] if valObj.data['department_id'] is not None else 0
            post_id = valObj.data['post_id'] if valObj.data['post_id'] is not None else 0
            name = valObj.data['name'] if valObj.data['name'] is not None else ""
            start_time = valObj.data['start'] if valObj.data['start'] is not None else ""
            end_time = valObj.data['end'] if valObj.data['end'] is not None else ""
            if not flag:
                msg = "访问页码错误，请确认"
                error_code = 10100
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            result = []
            try:
                dt = datetime.now()
                rObj = Archives.objects.filter(delete_time=None).order_by("job_number", "id")
                if department_id:
                    rObj = rObj.filter(department_id = department_id)
                if status:
                    rObj = rObj.filter(status = status)
                if post_id:
                    rObj = rObj.filter(post_id = post_id)
                if name:
                    rObj = rObj.filter(name = name)

                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start + page_size]
                    for o1 in rObj:
                        samp = {}
                        samp['id'] = o1.id
                        samp['job_number'] = o1.job_number
                        samp['name'] = o1.name
                        samp['gender'] = o1.gender
                        depObj = Department.objects.get(id=o1.department_id)
                        samp['department_name'] = depObj.department_name
                        postObj = Post.objects.get(id=o1.post_id)
                        samp['post_name'] = postObj.post_name
                        arcstand = ArchivesSalaryStandard.objects.filter(archives_id=o1.id)
                        if arcstand.count()>0:
                            annual_salary = arcstand[0].annual_salary
                            samp['annual_salary'] = arcstand[0].annual_salary
                            samp['payment'] = arcstand[0].payment
                            samp['social_insurance_id'] = arcstand[0].social_insurance_id
                            samp['social_insurance_level'] = arcstand[0].social_insurance_level
                            samp['social_insurance_company'] = arcstand[0].social_insurance_company
                            samp['social_insurance_person'] = arcstand[0].social_insurance_person
                            samp['other_contributions_company'] = arcstand[0].other_contributions_company
                            samp['other_contributions_person'] = arcstand[0].other_contributions_person
                            samp['surplu_id'] = arcstand[0].surplu_id
                            samp['surplu_level'] = arcstand[0].surplu_level
                            samp['surplu_company'] = arcstand[0].surplu_company
                            samp['surplu_person'] = arcstand[0].surplu_person

                        else:
                            annual_salary = Decimal(0)
                            samp['annual_salary'] = None
                            samp['payment'] = None
                            samp['social_insurance_id'] = None
                            samp['social_insurance_level'] = None
                            samp['social_insurance_company'] = None
                            samp['social_insurance_person'] = None
                            samp['other_contributions_company'] = None
                            samp['other_contributions_person'] = None
                            samp['surplu_id'] = None
                            samp['surplu_level'] = None
                            samp['surplu_company'] = None
                            samp['surplu_person'] = None
                        arcDetail = ArchivesSalaryDetail.objects.filter(archives_id=o1.id)
                        if start_time:
                            arcDetail = arcDetail.filter(create_time__gt=start_time)
                        if end_time:
                            arcDetail = arcDetail.filter(create_time__gt=end_time)
                        calculated_salary = Decimal(0)
                        other_salary = Decimal(0)
                        deduction = Decimal(0)
                        comments = ''
                        real_salary = Decimal(0)
                        for one in arcDetail:
                            calculated_salary += one.calculated_salary
                            other_salary += one.other_salary
                            comments =comments + one.comments +"|"
                            real_salary += one.real_salary
                        samp['calculated_salary'] = calculated_salary
                        samp['other_salary'] = other_salary
                        samp['deduction'] = deduction
                        samp['comments'] = comments
                        samp['real_salary'] = real_salary
                        if annual_salary:
                            samp['de_annual_salary'] = annual_salary - real_salary
                        else:
                            samp['de_annual_salary'] = 0
                        samp["status"] = o1.status
                        result.append(samp)
                    temp = {}
                    temp["data"] = result
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = []
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
            except:
                msg = "未找到对应的工号"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


# 订单分析
class showOrderStaticView(APIView):
    # 获取确认报价
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = showOrderStaticSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                if order_type != 0:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(custom=order_custom)
                if price_code:
                    rObj = rObj.filter(price_code=price_code)
                if dhkhao:
                    rObj = rObj.filter(dhkhao=dhkhao)
                if brand:
                    rObj = rObj.filter(brand=brand)

                samp = []
                for one in rObj:
                    zamp = {}
                    zamp["order_id"] = one.id
                    zamp["create_time"] = one.create_time
                    zamp["indicate_time"] = one.indicate_time
                    zamp["order_type"] = one.order_type
                    zamp["custom"] = one.custom
                    zamp["price_code"] = one.price_code
                    zamp["dhkhao"] = one.dhkhao
                    zamp["brand"] = one.brand
                    zamp["goods_name"] = one.goods_name
                    zamp["receivable"] = "未确认"
                    zamp["payable "] = "未确认"
                    zamp["invoice_status "] = "未确认"
                    zamp["status"] = "订单状态"
                    samp.append(zamp)

                temp = {}
                temp["data"] = samp
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
# 工厂生产汇总


class showFXFactoryMakeOneView(APIView):
    # 获取订单 订单出货方案
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderObj = PlanOrder.objects.get(id=nid)
                facObj = FactoryMake.objects.filter(delete_time=None,order_id=nid)
                coop_mode = ""
                make_factory = ""
                ticketing_custom = ""

                samplist=[]
                for one in facObj:
                    coop_mode += one.coop_mode
                    ticketing_custom += one.ticketing_custom
                    make_factory += one.make_factory
                    samp={}
                    samp['coop_mode'] = one.coop_mode
                    samp['make_factory'] = one.make_factory
                    samp['ticketing_custom'] = one.ticketing_custom

                    rObj = FactoryMakeLine.objects.filter(delete_time=None,factory_make_id =one.id).order_by('order_line_id','color', 'specs')
                    if rObj.count()>0:
                        zemp = []
                        for one1 in rObj:
                            jamp={}
                            jamp['color'] = one1.color
                            jamp['color_name'] = one1.color_name
                            jamp['color_num'] = one1.color_num
                            jamp['specs'] = one1.specs
                            jamp['contract_num'] = one1.contract_num
                            jamp['short_overflow'] = one1.short_overflow
                            jamp['short_overflow_direct'] = one1.short_overflow_direct
                            jamp['short_overflow_send'] = 0.05
                            jamp['order_num'] = one1.order_num
                            jamp['make_num'] = one1.make_num
                            jamp['inspect_num'] = one1.inspect_num
                            jamp['b_num'] = one1.b_num
                            try:
                                jamp['a_num'] = one1.make_num - one1.b_num
                                jamp['recover_b_num'] = one1.recover_b_num
                                jamp['all_b_num'] = one1.recover_b_num + one1.b_num
                                jamp['in_a_b_lv'] = jamp['a_num']/one1.b_num
                                jamp['make_a_b_lv'] = one1.make_num/jamp['all_b_num']
                            except:
                                jamp['a_num'] = 0
                                jamp['recover_b_num'] = 0
                                jamp['all_b_num'] = 0
                                jamp['in_a_b_lv'] = None
                                jamp['make_a_b_lv'] = None
                            zemp.append(jamp)
                        samp['out_stock'] = zemp
                    else:
                        samp['out_stock'] = []
                        samp['short_overflow'] = one.short_overflow
                    samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                temp['work_type'] = orderObj.work_type
                temp['o_order_type'] = orderObj.order_type
                temp['coop_mode'] = coop_mode
                temp['ticketing_custom'] = ticketing_custom
                temp['make_factory'] = make_factory
                temp['merchant'] = "南通风尚国际"
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的出货方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class shipmentFXSureOneView(APIView):
    # 获取生产用料分析
    @csrf_exempt
    def get(self, request, nid):
        try:
            # 加工工厂数据
            mObj = FactoryMake.objects.filter(delete_time=None, order_id=nid)
            fac_name = []
            coop_mode = ""
            inspect_num = 0
            b_num = 0
            make_num = 0
            for o1 in mObj:
                fac_name.append(o1.make_factory)
                coop_mode += o1.coop_mode + "|"
                mlineObj = FactoryMakeLine.objects.filter(delete_time=None, factory_make_id=o1.id)
                for o2 in mlineObj:
                    if o2.inspect_num:
                        inspect_num += o2.inspect_num
                        make_num += o2.inspect_num
                    if o2.b_num:
                        b_num += o2.b_num
                        make_num += o2.b_num
            orderClothOne = OrderClothShip.objects.filter(order_id=nid,delete_time=None)
            orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
            orderClothShip = OrderClothShip.objects.filter(delete_time=None,order_id=nid).order_by("order_cloth_id","supplier")
            samplist=[]
            for one in orderClothShip:
                samp={}
                samp['cloth_type'] = one.cloth_type
                samp['cloth_cat'] = one.cloth_cat
                samp['cloth_name'] = one.cloth_name
                samp['delivery_type'] = one.delivery_type
                samp['delivery_name'] = one.delivery_name
                samp['is_inspect'] = one.is_inspect
                samp['buy_all_num'] = one.buy_all_num
                samp['loss_lv'] = one.loss_lv
                samp['supplier'] = one.supplier
                try:
                    samp['make_all_use'] = one.buy_all_num
                    samp['send_all_use'] = round(Decimal(inspect_num/make_num)*one.buy_all_num,2)
                    planM = PlanMaterial.objects.get(id=one.plan_material_id)
                    error_num = one.buy_all_num - planM.m_use
                    samp['make_one_error_num'] = error_num/make_num
                    samp['send_one_error_num'] = error_num/inspect_num
                    samp['make_all_error_num'] =error_num
                    samp['send_all_error_num'] = round(Decimal(inspect_num / make_num) * error_num, 2)
                except:
                    samp['make_all_use'] = None
                    samp['send_all_use'] = None
                    samp['make_one_error_num'] = None
                    samp['send_one_error_num'] = None
                    samp['make_all_error_num'] = None
                    samp['send_all_error_num'] = None
                samp['order_cloth_ship_id'] = one.id
                rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=one.order_cloth_id,order_cloth_ship_id=one.id).order_by('color', 'specs')
                sub_data = []
                for one1 in rObj:
                    zamp = {}
                    zamp["order_cloth_ship_line_id"] = one1.id
                    zamp['color'] = one1.color
                    zamp['color_num'] = one1.color_num
                    zamp['guige'] = one1.guige
                    zamp['specs'] = one1.specs
                    zamp['buy_num'] = one1.buy_num
                    zamp['provide_num'] = one1.provide_num
                    zamp['provide_time'] = one1.provide_time
                    zamp['sample_send_time'] = one1.sample_send_time
                    zamp['sure_comment'] = one1.sure_comment
                    zamp['is_sure'] = one1.is_sure
                    sub_data.append(zamp)
                samp['sub_data'] = sub_data
                samplist.append(samp)


            temp = {}
            temp["data"] = samplist
            temp["orderObj"] = model_to_dict(orderObj)
            temp['fac_name'] = fac_name
            temp['coop_mode'] = coop_mode
            temp['make_num'] = make_num
            temp['inspect_num'] = inspect_num
            temp['b_num'] = b_num
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的面辅料采购"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class shipmentFXInSureOneView(APIView):
    # 获取生产用料分析
    @csrf_exempt
    def get(self, request, nid):
        try:
            # 加工工厂数据
            mObj = FactoryMake.objects.filter(delete_time=None, order_id=nid)
            fac_name = []
            coop_mode = ""
            inspect_num = 0
            b_num = 0
            make_num = 0
            for o1 in mObj:
                fac_name.append(o1.make_factory)
                coop_mode += o1.coop_mode + "|"
                mlineObj = FactoryMakeLine.objects.filter(delete_time=None, factory_make_id=o1.id)
                for o2 in mlineObj:
                    if o2.inspect_num:
                        inspect_num += o2.inspect_num
                        make_num += o2.inspect_num
                    if o2.b_num:
                        b_num += o2.b_num
                        make_num += o2.b_num
            orderClothOne = OrderClothShip.objects.filter(order_id=nid,delete_time=None)
            orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
            orderClothShip = OrderClothShip.objects.filter(delete_time=None,order_id=nid).order_by("order_cloth_id","supplier")
            samplist=[]
            new_num = 0
            new_amount = Decimal(0)
            all_cloth_amount = Decimal(0)
            for one in orderClothShip:
                all_cloth_amount +=  one.all_amount
                samp={}
                samp['cloth_type'] = one.cloth_type
                samp['cloth_cat'] = one.cloth_cat
                samp['cloth_name'] = one.cloth_name
                samp['delivery_type'] = one.delivery_type
                samp['delivery_name'] = one.delivery_name
                samp['is_inspect'] = one.is_inspect
                samp['buy_all_num'] = one.buy_all_num
                samp['loss_lv'] = one.loss_lv
                samp['supplier'] = one.supplier
                samp['all_amount'] = one.all_amount
                try:
                    samp['make_all_loss'] = round(one.buy_all_num*one.loss_lv/inspect_num,2)
                    samp['send_all_loss'] = round(one.buy_all_num*one.loss_lv/make_num,2)
                    samp['make_one_price'] = round(one.all_amount/make_num,2)
                    samp['send_one_price'] = round(one.all_amount/inspect_num,2)
                except:
                    samp['make_all_loss'] = None
                    samp['send_all_loss'] = None
                    samp['make_one_price'] = None
                    samp['send_one_price'] = None
                samp['is_new'] = one.is_new
                if one.is_new == 1:
                    new_num += 1
                    new_amount = one.all_amount

                samp['order_cloth_ship_id'] = one.id
                rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=one.order_cloth_id,order_cloth_ship_id=one.id).order_by('color', 'specs')
                sub_data = []
                for one1 in rObj:
                    zamp = {}
                    zamp["order_cloth_ship_line_id"] = one1.id
                    zamp['color'] = one1.color
                    zamp['color_num'] = one1.color_num
                    zamp['guige'] = one1.guige
                    zamp['specs'] = one1.specs
                    zamp['buy_num'] = one1.buy_num
                    zamp['provide_num'] = one1.provide_num
                    zamp['provide_time'] = one1.provide_time
                    zamp['sample_send_time'] = one1.sample_send_time
                    zamp['price'] = one1.price
                    zamp['inspect_num'] = inspect_num
                    zamp['make_num'] = make_num
                    zamp['sure_comment'] = one1.sure_comment
                    zamp['is_sure'] = one1.is_sure
                    sub_data.append(zamp)
                samp['sub_data'] = sub_data
                samplist.append(samp)


            temp = {}
            temp["data"] = samplist
            temp["orderObj"] = model_to_dict(orderObj)
            temp['fac_name'] = fac_name
            temp['coop_mode'] = coop_mode
            temp['make_num'] = make_num
            temp['inspect_num'] = inspect_num
            temp['b_num'] = b_num
            temp['new_num'] = new_num
            temp['new_amount'] = new_amount
            temp['new_lv'] = round(new_amount/all_cloth_amount,2)
            temp['error_code'] = 0
            temp['message'] = "成功"
            temp['request'] = request.method + '  ' + request.get_full_path()
            return Response(temp)
        except:
            msg = "未找到对应的面辅料采购"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    @csrf_exempt
    def post(self, request,nid):
        sn = "0"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.data
        valObj = orderClothSerializer(data=request.data)
        if valObj.is_valid():
            work_type = valObj.data['work_type'] if valObj.data['work_type'] is not None else ""
            dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderClothLineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
                subdata = done['sub_data']
                s_flag = 0
                s_num = 0
                for sdone in subdata:
                    s_num = s_num + 1
                    valObjline = orderClothLineSubSerializer(data=sdone)
                    if not valObjline.is_valid():
                        s_flag = 1
                        samp = {}
                        samp['msg'] = valObjline.errors
                        samp['key_num'] = s_num
                        l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0 and s_flag == 0:
                for done in dataone:
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderCloth.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = OrderCloth()
                                bObj.create_time = dt
                        except:
                            bObj = OrderCloth()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        bObj.plan_id = data['plan_id']
                        bObj.plan_material_id = done['plan_material_id']
                        bObj.cloth_type = done['cloth_type']
                        bObj.cloth_cat = done['cloth_cat']
                        bObj.cloth_name = done['cloth_name']
                        bObj.delivery_type = done['delivery_type']
                        bObj.delivery_name = done['delivery_name']
                        try:
                            bObj.is_inspect = done['is_inspect']
                        except:
                            bObj.is_inspect = 0
                        bObj.buy_all_num = done['buy_all_num']
                        bObj.loss_lv = done['loss_lv']
                        bObj.is_new = 1
                        bObj.save()
                        if mid:
                            order_cloth_id = mid
                        else:
                            ocOne = OrderCloth.objects.latest("id")
                            order_cloth_id = ocOne.id
                        # 保存发货方案
                        try:
                            if not mid:
                                nbObj = OrderClothShip()
                                planmObj = PlanMaterial.objects.filter(id=done['plan_material_id'], delete_time=None)
                                if planmObj.count() > 0:
                                    nbObj.supplier = planmObj[0].complayer
                                nbObj.plan_material_id = done['plan_material_id']
                                nbObj.create_time = dt
                                nbObj.order_id = data['order_id']
                                nbObj.plan_id = data['plan_id']
                                nbObj.cloth_type = done['cloth_type']
                                nbObj.cloth_cat = done['cloth_cat']
                                nbObj.cloth_name = done['cloth_name']
                                nbObj.delivery_type = done['delivery_type']
                                nbObj.delivery_name = done['delivery_name']
                                try:
                                    nbObj.is_inspect = done['is_inspect']
                                except:
                                    nbObj.is_inspect = 0
                                nbObj.buy_all_num = done['buy_all_num']
                                nbObj.loss_lv = done['loss_lv']
                                nbObj.order_cloth_id = order_cloth_id
                                nbObj.is_new = 1
                                nbObj.save()
                            if mid:
                                ocsObj = OrderClothShip.objects.filter(order_cloth_id=mid)
                                for ocs in ocsObj:
                                    planmObj = PlanMaterial.objects.filter(id=done['plan_material_id'],
                                                                           delete_time=None)
                                    if planmObj.count() > 0:
                                        ocs.supplier = planmObj[0].complayer
                                    ocs.plan_material_id = done['plan_material_id']
                                    ocs.create_time = dt
                                    ocs.order_id = data['order_id']
                                    ocs.plan_id = data['plan_id']
                                    ocs.cloth_type = done['cloth_type']
                                    ocs.cloth_cat = done['cloth_cat']
                                    ocs.cloth_name = done['cloth_name']
                                    try:
                                        ocs.is_inspect = done['is_inspect']
                                    except:
                                        ocs.is_inspect = 0
                                    ocs.buy_all_num = done['buy_all_num']
                                    ocs.loss_lv = done['loss_lv']
                                    ocs.save()
                        except:
                            pass
                        # 保存面辅料的sku
                        subdata = done['sub_data']
                        for sub in subdata:
                            try:
                                s_id = sub["id"]
                                if s_id:
                                    sbObj = OrderClothLine.objects.get(id=s_id)
                                    sbObj.update_time = dt
                                else:
                                    sbObj = OrderClothLine()
                                    sbObj.create_time = dt
                            except:
                                sbObj = OrderClothLine()
                                sbObj.create_time = dt
                            sbObj.order_id = data['order_id']
                            sbObj.order_cloth_id = order_cloth_id
                            if done['cloth_type'] == 4:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                                sbObj.specs = sub['specs']
                                outStackObj = OutStock.objects.filter(order_id=data['order_id'], color=sub['color'],
                                                                      color_num=sub['color_num'], specs=sub['specs'])
                                order_num = 0
                                for one in outStackObj:
                                    order_num += one.order_num
                                sbObj.order_num = order_num
                            if done['cloth_type'] == 3:
                                sbObj.specs = sub['specs']
                                outStackObj = OutStock.objects.filter(order_id=data['order_id'], specs=sub['specs'])
                                order_num = 0
                                for one in outStackObj:
                                    order_num += one.order_num
                                sbObj.order_num = order_num
                            if done['cloth_type'] == 2:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
                                outStackObj = OutStock.objects.filter(order_id=data['order_id'], color=sub['color'],
                                                                      color_num=sub['color_num'])
                                order_num = 0
                                for one in outStackObj:
                                    order_num += one.order_num
                                sbObj.order_num = order_num
                            if done['cloth_type'] == 1:
                                orderOne = PlanOrder.objects.get(id=data['order_id'])
                                sbObj.order_num = orderOne.order_num
                            sbObj.guige = sub['guige']
                            sbObj.buy_num = sub['buy_num']
                            sbObj.is_inspect = sub['is_inspect']
                            sbObj.save()
                            if s_id:
                                order_cloth_line_id = s_id
                            else:
                                ocOne = OrderClothLine.objects.latest("id")
                                order_cloth_line_id = ocOne.id
                            # 保存发货方案的sku
                            if not mid:
                                ncOne = OrderClothShip.objects.latest("id")
                                try:
                                    nblObj = OrderClothLineShip()
                                    nblObj.create_time = dt
                                    nblObj.order_id = data['order_id']
                                    nblObj.order_cloth_id = order_cloth_id
                                    if done['cloth_type'] == 4:
                                        nblObj.color = sub['color']
                                        nblObj.color_num = sub['color_num']
                                        nblObj.specs = sub['specs']
                                    if done['cloth_type'] == 3:
                                        nblObj.specs = sub['specs']
                                    if done['cloth_type'] == 2:
                                        nblObj.color = sub['color']
                                        nblObj.color_num = sub['color_num']
                                    nblObj.guige = sub['guige']
                                    nblObj.buy_num = sub['buy_num']
                                    nblObj.order_cloth_line_id = order_cloth_line_id
                                    nblObj.order_cloth_ship_id = ncOne.id
                                    if planmObj.count() > 0:
                                        nblObj.price = planmObj[0].price
                                        nblObj.amount = planmObj[0].total
                                    nblObj.save()
                                except:
                                    pass
                            if mid:
                                if s_id:
                                    ocslObj = OrderClothLineShip.objects.filter(order_cloth_line_id=s_id,
                                                                                order_cloth_id=order_cloth_id)
                                    for ocsl in ocslObj:
                                        ocsl.buy_num = sub['buy_num']
                                        ocsl.guige = sub['guige']
                                        ocsl.save()
                    except:
                        msg = "参数错误"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                try:
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.is_buyprogram = 1
                    bg_num = OrderCloth.objects.filter(order_id=data['order_id'], delete_time=None).count()
                    order.buyprogram_num = bg_num
                    if dhkhao:
                        order.dhkhao = dhkhao
                    if work_type:
                        order.work_type = work_type
                    order.save()
                except:
                    pass
                msg = "创建/编辑面辅料采购"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            else:
                msg = l_msg
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class showFXOutStockOneView(APIView):
    # 获取订单 订单出货方案
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderObj = PlanOrder.objects.get(id=nid)
                orderline = PlanOrderLine.objects.filter(delete_time=None,order_id=nid)
                samplist=[]
                for one in orderline:
                    samp={}
                    samp['order_custom'] = one.order_custom
                    samp['order_type'] = one.order_type
                    samp['contract_num'] = one.contract_num
                    samp['order_line_id'] = one.id
                    samp['order_price_type'] = one.order_price_type
                    samp['is_sure_price'] = one.is_sure_price
                    samp['order_price'] = one.order_price
                    samp['pay_y_amount'] = one.pay_y_amount
                    rObj = OutStock.objects.filter(delete_time=None, order_line_id=one.id).order_by('color', 'specs')
                    if rObj.count()>0:
                        zemp = []
                        for one1 in rObj:
                            jamp={}
                            jamp['color'] = one1.color
                            jamp['color_name'] = one1.color_name
                            jamp['color_num'] = one1.color_num
                            jamp['specs'] = one1.specs
                            jamp['contract_num'] = one1.contract_num
                            jamp['short_overflow'] = one1.short_overflow
                            jamp['short_overflow_direct'] = one1.short_overflow_direct
                            jamp['order_num'] = one1.order_num
                            # 送检数量
                            # b品数量
                            faclineObj = FactoryMakeLine.objects.filter(order_line_id=one.id,color=one1.color,color_num=one1.color_num,specs=one1.specs)
                            make_num = 0
                            inspect_num = 0
                            b_num = 0
                            for one2 in faclineObj:
                                if one2.make_num:
                                    make_num += one2.make_num
                                if one2.b_num:
                                    b_num += one2.b_num
                                if one2.inspect_num:
                                    inspect_num += one2.inspect_num


                            jamp['inspect_num'] = inspect_num
                            jamp['b_num'] = b_num
                            a_num = make_num -b_num
                            jamp['a_b_lv'] =a_num/b_num
                            # 船样数量
                            cysamp_num = 0
                            planSamp = PlanClothSampleLine.objects.filter(sample_type="船样",plan_id=orderObj.plan_id)
                            for one3 in planSamp:
                                plansampNum = PlanClothSampleNumber.objects.filter(pcsl_id=one3.id,sub_color_name=one1.color,sub_specs_name=one1.specs)
                                for one4 in plansampNum:
                                    if one4.num:
                                        cysamp_num +=one4.num
                            jamp['cysamp_num'] = cysamp_num
                            zemp.append(jamp)
                        samp['out_stock'] = zemp
                    else:
                        samp['out_stock'] = []
                        samp['short_overflow'] = one.short_overflow
                    samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                facmObj = FactoryMake.objects.filter(order_id = nid)
                coop_mood = ""
                make_factory = ""
                ticketing_custom = ""

                for one5 in facmObj:
                    coop_mood += one5.coop_mode
                    ticketing_custom += one5.ticketing_custom
                    make_factory += one5.make_factory

                temp['work_type'] = orderObj.work_type
                temp['o_order_type'] = orderObj.order_type
                temp['coop_mood'] = coop_mood
                temp['ticketing_custom'] = ticketing_custom
                temp['make_factory'] = make_factory
                temp['merchant'] = "南通风尚国际"
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)
            except:
                msg = "未找到对应的出货方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)




##############################################################订单分析-其他
class newOtherAccountsView(APIView):
    # 添加/编辑 生产组织其他应付
    @csrf_exempt
    def post(self, request):
        sn = "50301"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        data  = request.data
        try:
            order_id = data['order_id']
        except:
            msg = "请输入订单id"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        dataone =data['data']
        for done in dataone:
            d_num = d_num + 1
            valObjline = sampOtherAcountOneSerializer(data=done)
            if not valObjline.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObjline.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        ##############保存装箱指示#############################
        if d_flag == 0:
            for done in dataone:
                try:
                    mid =done['id']
                    if mid:
                        bObj = OtherAccountNew.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = OtherAccountNew()
                        bObj.create_time = dt
                    bObj.order_id = data['order_id']
                    bObj.custom = done['custom']
                    bObj.pay_custom = done['pay_custom']
                    bObj.pay_comment = done['pay_comment']
                    bObj.price_type = done['price_type']
                    bObj.pay_num = done['pay_num']
                    bObj.pay_price = done['pay_price']
                    bObj.pay_amount = done['pay_amount']
                    bObj.finish_amount = Decimal(0)
                    bObj.is_sure = 1
                    bObj.is_finish_pay = 0
                    bObj.save()
                except:
                    msg = "id参数错误"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "编辑其他应收款"
            error_code = 0
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        else:
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)



class newOtherOneAccountsView(APIView):
    @csrf_exempt
    def get(self, request,nid):
        sn = "60104"
        ret, msg = checkPermission(request, sn)
        if ret == False:
            msg = msg
            error_code = 10001
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
        data = request.query_params
        valObj = showReceiptDataSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                all_amount = Decimal(0)
                samp = []
                # 加工工厂数据
                mObj = FactoryMake.objects.filter(delete_time=None, order_id=nid)
                fac_name = []
                coop_mode = ""
                inspect_num = 0
                b_num = 0
                make_num = 0
                for o1 in mObj:
                    fac_name.append(o1.make_factory)
                    coop_mode += o1.coop_mode + "|"
                    mlineObj = FactoryMakeLine.objects.filter(delete_time=None, factory_make_id=o1.id)
                    for o2 in mlineObj:
                        if o2.inspect_num:
                            inspect_num += o2.inspect_num
                            make_num += o2.inspect_num
                        if o2.b_num:
                            b_num += o2.b_num
                            make_num += o2.b_num

                prodObj = ProductPayStatic.objects.filter(type=3, delete_time=None, order_id=nid)
                for o1 in prodObj:
                    zamp = {}
                    zamp['pay_project'] = o1.pay_project
                    zamp['price_type'] = o1.price_type
                    zamp['pay_price'] = o1.pay_price
                    zamp['pay_num'] = o1.pay_num
                    zamp['pay_amount'] = o1.pay_amount
                    if o1.pay_amount:
                        all_amount += o1.pay_amount
                    zamp['receip_custom'] = o1.custom
                    zamp['pay_custom'] = o1.pay_custom
                    zamp['fee_no'] = o1.fee_no
                    zamp['fee_amount'] = o1.fee_amount
                    zamp['fee_no_status'] = o1.fee_no_status
                    zamp["is_new"] = 0
                    samp.append(zamp)
                orderPay = OrderPay.objects.filter(order_id=nid)
                for o2 in orderPay:
                    zamp = {}
                    zamp['pay_project'] = o2.pay_content
                    zamp['price_type'] = o2.pay_type
                    zamp['pay_price'] = o2.pay_price
                    zamp['pay_num'] = o2.pay_num

                    zamp['pay_amount'] = o2.amount
                    if o2.amount:
                        all_amount +=  o2.amount
                    zamp['receip_custom'] = o2.custom
                    zamp['pay_custom'] = o2.provide_custom
                    zamp['fee_no'] = o2.fee_no
                    zamp['fee_amount'] = o2.fee_amount
                    zamp['fee_no_status'] = o2.fee_no_status
                    zamp["is_new"] = 0
                    samp.append(zamp)
                sampObj = SamplePayStatic.objects.filter(order_id=nid)
                for o3 in sampObj:
                    zamp = {}
                    zamp["status"] = "订单状态"
                    zamp['pay_project'] = o3.pay_comment
                    zamp['price_type'] = o3.price_type
                    zamp['pay_price'] = o3.pay_price
                    zamp['pay_num'] = o3.pay_num
                    zamp['pay_amount'] = o3.pay_amount
                    if o3.pay_amount:
                        all_amount +=  o3.pay_amount
                    zamp['receip_custom'] = o3.custom
                    zamp['pay_custom'] = o3.pay_custom
                    zamp['fee_no'] = o3.fee_no
                    zamp['fee_amount'] = o3.fee_amount
                    zamp['fee_no_status'] = o3.fee_no_status
                    zamp["is_new"] = 0
                    samp.append(zamp)
                newObj = OtherAccountNew.objects.filter(order_id=nid)
                new_amount = Decimal(0)
                for o4 in newObj:
                    zamp = {}
                    zamp['pay_project'] = o4.pay_comment
                    zamp['price_type'] = o4.price_type
                    zamp['pay_price'] = o4.pay_price
                    zamp['pay_num'] = o4.pay_num
                    zamp['pay_amount'] = o4.pay_amount
                    zamp['receip_custom'] = o4.custom
                    zamp['pay_custom'] = o4.pay_custom
                    if o4.pay_amount:
                        new_amount +=o4.pay_amount
                        all_amount += o4.pay_amount
                    zamp['fee_no'] = o4.fee_no
                    zamp['fee_amount'] = o4.fee_amount
                    zamp['fee_no_status'] = o4.fee_no_status
                    zamp["is_new"] = 1
                    samp.append(zamp)
                custom_dic,custom_list = getAllCustom(nid)
                temp = {}
                temp["data"] = samp
                temp['inspect_num'] = inspect_num
                temp['make_num'] = make_num
                temp['merchanrt'] = "南通风尚国际"
                temp['custom_dic'] =custom_dic
                temp['custom_list'] =custom_list
                temp['new_lv'] = round(new_amount/all_amount,2)
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = valObj.errors
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)





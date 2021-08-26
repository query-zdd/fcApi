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
# Create your views here.
############################订单管理-出货方案###############################################

class showOutStockView(APIView):
    # 添加/编辑 订单出货方案
    @csrf_exempt
    def post(self, request):
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
                    pgall = PlanOrderLine.objects.filter(order_id=data['order_id'])
                    pgone = PlanOrderLine.objects.filter(order_id=data['order_id'],is_pushprogram=1)
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
                        else:
                            samp['out_stock'] = []
                            samp['short_overflow'] = one.short_overflow
                        samplist.append(samp)

                temp = {}
                temp["data"] = samplist
                orderObj = PlanOrder.objects.get(id=nid)
                temp['orderObj'] = model_to_dict(orderObj)
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
                temp["data"] = samplist
                temp['work_type'] = orderObj.work_type
                temp['contract_num'] = orderObj.contract_num
                temp['order_num'] = orderObj.order_num
                temp['short_overflow_num'] = orderObj.order_num
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
                        samplist.append(samp)
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
                                ppObj = OrderLinePacking.objects.get(id=done['parent_id'])
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
        try:
            lineShipObj = OrderClothLineShip.objects.get(id=nid)
            purchasObj = PurchasingRecords.objects.filter(delete_time=None,order_cloth_line_ship_id=nid)
            orderObj = PlanOrder.objects.get(id=lineShipObj.order_id)
            temp = {}
            temp["data"] = purchasObj.values()
            lineshipdic = model_to_dict(lineShipObj)
            if not lineshipdic["add_up_num"]:
                lineshipdic["add_up_num"] = 0
            if not lineshipdic['short_send_num']:
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
                rObj = PlanOrder.objects.filter(delete_time=None,real_start_date=None)
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
                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start + page_size]
                    data = []
                    for one in rObj:
                        samp = {}
                        samp['order_id'] = one.id
                        samp['plan_id'] = one.plan_id
                        samp['create_time'] = one.create_time
                        samp['price_code'] = one.price_code
                        samp['dhkhao'] = one.dhkhao
                        samp['work_type'] = one.work_type
                        samp['leader'] = one.leader
                        #发货倒计时
                        try:
                            orderlineObj = PlanOrderLine.objects.filter(order_id = one.id)
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
                        zamp["fm_num"] = fmObj.count()
                        sure_plan_num = 0
                        sure_real_num = 0
                        for one2 in fmObj:
                            if one2.plan_start_date:
                                sure_plan_num = sure_plan_num + 1
                                down_data = downDay(one2.plan_start_date,dtnow)
                                down_list.append(down_data)
                            if one2.real_start_date:
                                sure_real_num = sure_real_num + 1
                        zamp["sure_plan_num"] = sure_plan_num
                        zamp["sure_real_num"] = sure_real_num
                        zamp["fmObjLine"] = fmObj.values()
                        samp["fmObj"] = zamp
                        if down_list:
                            samp["down_day"] = min(down_list)
                        else:
                            samp["down_day"] = None
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
                if rObj.count() > start:
                    rObj = rObj.all()[start:start + page_size]
                    rObj = rObj.values()
                    for one in rObj:
                        one["sub_order_line"] = PlanOrderLine.objects.filter(order_id=one["id"]).values()
                    temp = {}
                    temp["data"] = rObj
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
        data = request.data
        try:
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
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
                        mid = done["order_line_id"]
                        bObj = PlanOrderLine.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.indicate_time = done['indicate_time']
                        bObj.delivery_way = done['delivery_way']
                        bObj.transportation = done['transportation']
                        bObj.exporter_way = done['exporter_way']
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
                rObj = PlanOrderLine.objects.filter(delete_time=None).order_by("inspect_time","order_id")
                order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                if order_type:
                    rObj = rObj.filter(order_type=order_type)
                if order_custom:
                    rObj = rObj.filter(order_custom=order_custom)
                if dhkhao:
                    mkObj = PlanOrder.objects.filter(dhkhao=dhkhao)
                    oids = [one.id for one in mkObj]
                    rObj = rObj.filter(order_id__in=oids)
                if price_code:
                    mkObj = PlanOrder.objects.filter(price_code=price_code)
                    oids = [one.id for one in mkObj]
                    rObj = rObj.filter(order_id__in=oids)
                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start + page_size]
                    rObj = rObj.values()
                    temp = {}
                    temp["data"] = rObj
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
        data = request.data
        valObj = reightSpaceSerializer(data=request.data)
        dt = datetime.now()
        if valObj.is_valid():
            try:
                mid = valObj.data['id']
                if mid:
                    bObj = ReightSpace.objects.get(id=mid)
                else:
                    bObj = ReightSpace()
                bObj.update_time = dt
                bObj.indicate_time = data['indicate_time']
                bObj.shou_huo_term_id = valObj.data['shou_huo_term_id']
                bObj.shou_huo_term_name = valObj.data['shou_huo_term_name']
                bObj.space_name = valObj.data['space_name']
                bObj.exporter_way = data['exporter_way']
                bObj.pol = data['pol']
                bObj.pod = data['pod']
                bObj.transportation = data['transportation']
                bObj.order_line_ids = data['order_line_ids']
                bObj.status = 0
                bObj.save()
                if mid:
                    reight_space_id = mid
                else:
                    bOne = ReightSpace.objects.latest("id")
                    reight_space_id = bOne.id
                try:
                    line_id_line =  data['order_line_ids'].split(",")
                    for l_id in line_id_line:
                        if l_id:
                            planLine = PlanOrderLine.objects.get(id=l_id)
                            planLine.reight_space_id = reight_space_id
                            planLine.save()
                except:
                    pass
                msg = "编辑指示预定仓位"
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
    # 获取预定仓位
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = reightSpaceLineSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None)
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
                orderLine = PlanOrderLine.objects.filter(delete_time=None,order_id__in=order_ids).order_by("-reight_space_id","order_id")
                temp = {}
                data = orderLine.values()
                for one in data:
                    if one["reight_space_id"]:
                        onespcace = ReightSpace.objects.get(id=one["reight_space_id"])
                        one["reight_space_status"] = onespcace.status
                    else:
                        one["reight_space_status"] = onespcace.status
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
        try:
            rObj = ReightSpace.objects.get(id=nid)
            ids = rObj.order_line_ids.split(",")
            orderLine = PlanOrderLine.objects.filter(delete_time=None,order_id__in=ids).order_by("-reight_space_id","order_id")
            temp = {}
            temp["data"] = orderLine.values()
            temp['shou_huo_term_name'] = rObj.shou_huo_term_name
            temp['space_name'] = rObj.space_name
            temp['exporter_way'] = rObj.exporter_way
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

    @csrf_exempt
    def post(self, request, nid):
        valObj = reightSpaceOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                dt = datetime.now()
                bObj = ReightSpace.objects.get(id=nid)
                bObj.reight_s_time = dt
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
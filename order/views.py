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
                        for one1 in xfmlObj:
                            one1.delete()
                            one1.save()
                        one.delete()
                        one.save()
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
                                #编辑时，删除已有的sku数据
                                nbObj = OrderClothShip.objects.filter(order_cloth_id=mid)
                                for one in nbObj:
                                    nbObjline = OrderClothLineShip.objects.filter(order_cloth_id=mid)
                                    for sub in nbObjline:
                                        sub.delete()
                                        sub.save()
                                    one.delete()
                                    one.save()
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
                        bObj.is_inspect = done['is_inspect']
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
                            nbObj.is_inspect = done['is_inspect']
                            nbObj.buy_all_num = done['buy_all_num']
                            nbObj.loss_lv = done['loss_lv']
                            nbObj.order_cloth_id = order_cloth_id
                            nbObj.save()
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
                            sbObj.save()
                            if s_id:
                                order_cloth_line_id = s_id
                            else:
                                ocOne = OrderClothLine.objects.latest("id")
                                order_cloth_line_id = ocOne.id
                            #保存发货方案的sku
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


class orderClothOneView(APIView):
    # 获取订单 面辅料采购
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                orderObj = PlanOrder.objects.get(delete_time=None, id=nid)
                orderCloth = OrderCloth.objects.filter(order_id=nid)
                planObj = Plan.objects.get(id=orderObj.plan_id)
                fmObj = FactoryMake.objects.filter(order_id=nid)
                coop_mode = ''
                ticketing_custom = ''
                for o in fmObj:
                    coop_mode +=o.coop_mode+'|'
                    ticketing_custom +=o.ticketing_custom+'|'
                samplist=[]
                for one in orderCloth:
                    samp={}
                    samp['plan_material_id'] = one.plan_material_id
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
                temp['coop_mode'] = coop_mode
                temp['ticketing_custom'] = ticketing_custom
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
                notesAll = ClothNotes.objects.filter(delete_time=None).order_by('category_id', 'weight')
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
                notes_all_num = 0
                notes_sure_num = 0
                notes_nosure_num = 0
                orderNote = OrderNotes.objects.filter(plan_id=nid)
                note_id_list = [one.notes_id for one in orderNote]
                notesAll = ClothNotes.objects.filter(delete_time=None, id__in=note_id_list).order_by('category_id','weight')
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
                temp = {}
                temp["data"] =noteslist
                temp['notes_nosure_num'] = notes_nosure_num
                temp['notes_sure_num'] = notes_sure_num
                temp['notes_all_num'] = notes_all_num
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
        valObj = orderNotesOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                notesAll = OtherNotes.objects.filter(delete_time=None).order_by('category_setting_id', 'weight')
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
        valObj = orderNotesOne1Serializer(data=request.query_params)
        if valObj.is_valid():
            try:
                notes_all_num = 0
                notes_sure_num = 0
                notes_nosure_num = 0
                orderNote = OrderNotesOther.objects.filter(plan_id=nid)
                note_id_list = [one.notes_id for one in orderNote]
                notesAll = OtherNotes.objects.filter(delete_time=None, id__in=note_id_list).order_by('category_setting_id','weight')
                noteslist  = notesAll.values()
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
    # 获取订单 发货方案
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
                    samp['id'] = one.id
                    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=nid,order_cloth_ship_id=one.id).order_by('color', 'specs')
                    samp['sub_data'] = rObj.values()
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
    # 添加/编辑 发货方案
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
            ##############保存出货方案#############################
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
        valObj = orderOutstockGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:

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
                    samp['id'] = one.id
                    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=one.order_cloth_id,order_cloth_ship_id=one.id).order_by('color', 'specs')
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
            temp = {}
            temp["data"] = purchasObj.values()
            temp["lineShipObj"] = model_to_dict(lineShipObj)
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
                    samp['plan_start_time'] = '2020-03-18'
                    samp['down_day'] = 3
                    samp['order_cloth_ship_id'] = one.id
                    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=one.order_cloth_id,order_cloth_ship_id=one.id).order_by('color', 'specs')
                    sure_num = 0
                    no_sure_num = 0
                    for one in rObj:
                        if one.is_sure == 1:
                            sure_num = sure_num + 1
                        else:
                            no_sure_num = no_sure_num + 1
                    samp['sure_num'] = sure_num
                    samp['no_sure_num'] = no_sure_num
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
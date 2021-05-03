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

# Create your views here.
############################订单管理-出货方案###############################################

class showOutStockView(APIView):
    # 添加/编辑 订单出货方案
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = orderOutstockSerializer(data=request.data)
        if valObj.is_valid():
            dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else 0
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderOutstockLineSerializer(data=done)
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
                                bObj = OutStock.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = OutStock()
                                bObj.create_time = dt
                        except:
                            bObj = OutStock()
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
                    # 更新orderline
                    orderline = PlanOrderLine.objects.get(id=data['order_line_id'])
                    orderline.is_pushprogram =1
                    orderline.short_overflow_direct = data['short_overflow_direct']
                    orderline.save()
                    # 更新order
                    order = PlanOrder.objects.get(id=data['order_id'])
                    order.is_pushprogram =1
                    pg_num = PlanOrderLine.objects.filter(order_id=data['order_id'],is_pushprogram=1).count()
                    order.pushprogram_num =pg_num
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
                        samp['order_line_id'] = one.id
                        rObj = OutStock.objects.filter(delete_time=None, order_line_id=one.id).order_by('color', 'specs')
                        samp['out_stock'] = rObj.values()
                        samplist.append(samp)

                temp = {}
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
                    try:
                        try:
                            mid = done["id"]
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
                        bObj.make_time = done['make_time']
                        bObj.make_factory = done['make_factory']
                        bObj.inspect_company = done['inspect_company']
                        bObj.order_admin = done['order_admin']
                        bObj.ticketing_custom = done['ticketing_custom']
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
                    order.work_type =data['work_type']
                    if dhkhao:
                        order.dhkhao = dhkhao
                    order.save()
                except:
                    pass
                msg = "创建/编辑工厂方案成功"
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
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                samplist = []
                fmObj = FactoryMake.objects.filter(delete_time=None,order_id=nid)
                samplist=[]
                for one in fmObj:
                    samp={}
                    samp['make_time'] = one.make_time
                    samp['make_factory'] = one.make_factory
                    samp['coop_mode'] = one.coop_mode
                    samp['inspect_company'] = one.inspect_company
                    samp['order_admin'] = one.order_admin
                    samp['ticketing_custom'] = one.ticketing_custom
                    samp['id'] = one.id
                    rObj = FactoryMakeLine.objects.filter(delete_time=None, factory_make_id=one.id).order_by('color', 'specs')
                    samp['sub_line'] = rObj.values()
                    samplist.append(samp)
                temp = {}
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
            dt = datetime.now()
            ##############保存出货方案#############################
            if d_flag == 0:
                for done in dataone:
                    try:
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
                        bObj.factory_make_id = data['factory_make_id']
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
                    # 更新orderline
                    orderline = PlanOrderLine.objects.get(id=data['order_line_id'])
                    orderline.is_work_progrem =1
                    orderline.save()
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
                samplist=[]
                for one in orderline:
                    samp={}
                    samp['order_custom'] = one.order_custom
                    samp['order_type'] = one.order_type
                    samp['order_line_id'] = one.id
                    rObj = FactoryMakeLine.objects.filter(delete_time=None, order_line_id=one.id).order_by('color', 'specs')
                    samp['machining_sub'] = rObj.values()
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
                            if done['cloth_type'] ==3:
                                sbObj.specs = sub['specs']
                            if done['cloth_type'] ==2:
                                sbObj.color = sub['color']
                                sbObj.color_num = sub['color_num']
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
            dataone = data['data']
            dt = datetime.now()
            for done in dataone:
                d_num = d_num + 1
                valObjline = orderNotesLineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
                if valObjline.is_valid():
                    try:
                        try:
                            mid = done["id"]
                            if mid:
                                bObj = OrderNotes.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                if valObjline.data['notes_id']:
                                    bList = OrderNotes.objects.filter(order_id=data['order_id'],
                                                                     order_cloth_id=data['order_cloth_id'],notes_id=valObjline.data['notes_id'])
                                    if bList.count()>0:
                                        bObj = bList[0]
                                        bObj.update_time = dt
                                    else:
                                        bObj = OrderNotes()
                                        bObj.create_time = dt
                        except:
                            bObj = OrderNotes()
                            bObj.create_time = dt
                        bObj.order_id = data['order_id']
                        bObj.order_cloth_id = data['order_cloth_id']
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

    # 获取订单 注意事项所有
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = orderNotesOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                notesAll = ClothNotes.objects.filter(delete_time=None).order_by('category_id', 'weight')
                noteslist = notesAll.values()
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
                    orderNote = OrderNotes.objects.filter(order_cloth_id=valObj.data['order_cloth_id'],
                                                          notes_id=one["id"], order_id=valObj.data['order_id'])
                    if orderNote.count() > 0:
                        one['people'] = orderNote[0].people
                        one['people_department'] = orderNote[0].people_department
                        one['people_post'] = orderNote[0].people_post
                        one['liuyan'] = orderNote[0].liuyan
                        one['beizhu'] = orderNote[0].beizhu
                        one['warm_time'] = orderNote[0].warm_time
                        one['warm_day_num'] = orderNote[0].warm_day_num
                        dt1 = datetime.now()
                        dt2 = orderNote[0].warm_time
                        one["down_days_num"] = downDay(dt1, dt2)
                        one['is_active'] = 1
                    else:
                        one['is_active'] = 0
                temp = {}
                temp["data"] = noteslist
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
                orderNote = OrderNotes.objects.filter(order_cloth_id=nid, order_id=nid)
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
                    orderNote =OrderNotes.objects.filter(order_cloth_id=nid, order_id=nid,notes_id=one['id'])
                    if orderNote.count()>0:
                        one['people'] = orderNote[0].people
                        one['people_department'] = orderNote[0].people_department
                        one['people_post'] = orderNote[0].people_post
                        one['liuyan'] = orderNote[0].liuyan
                        one['beizhu'] = orderNote[0].beizhu
                        one['warm_time'] = orderNote[0].warm_time
                        one['warm_day_num'] = orderNote[0].warm_day_num
                        dt1 = datetime.now()
                        dt2 = orderNote[0].warm_time
                        one["down_days_num"] = downDay(dt1,dt2)
                        one['is_active'] = 1
                    else:
                        one['is_active'] = 0
                temp = {}
                temp["data"] =noteslist
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
    dayNum = (d2.date()-d1.date()).days
    return dayNum


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
                        bObj.delivery_type = done['delivery_type']
                        bObj.delivery_name = done['delivery_name']
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
                orderClothShip = OrderClothShip.objects.filter(order_cloth_id=nid)
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
                    rObj = OrderClothLineShip.objects.filter(delete_time=None, order_cloth_id=nid,order_cloth_ship_id=one.id).order_by('color', 'specs')
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
                for one in orderLine:
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

                temp = {}
                temp["data"] = samplist
                temp["order_id"] = nid
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
        valObj = packingSublineSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
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
                        bObj.order_line_id = data['order_line_id']
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
                    o_pack = OrderLinePackingSub.objects.filter(order_line_id=one.id,out_stock_id=one.id)
                    if o_pack.count()>0:
                        samp = model_to_dict(o_pack[0])
                    else:
                        samp['parent_id'] = 0
                        samp['id'] = 0
                    samp['order_line_id'] = one.order_line_id
                    samp['color'] = one.color
                    samp['color_name'] = one.color_name
                    samp['color_num'] = one.color_num
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
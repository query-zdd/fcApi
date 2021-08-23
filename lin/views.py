from django.http import HttpResponse,request
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from order.utils import *
import requests
from datetime import *


from lin.utils import *
from secure.from_safe import *
from lin.models import *
from lin.exception import Error
from secure.upload.upload_image.config import  access_key,secret_key,base_url
from secure.serializers import zddpaginate
import random

# Create your views here.
#############################  基础资料  #########################################
from secure.upload.upload_image.token import get_token

def get_member_N():
    mObj = JobNumber.objects.get(id=1)
    try:
        if mObj.sort_type==0:
            num = random.randint(int(mObj.start_number),int(mObj.end_number))
        else:
            num = Archives.objects.all().count()+1
    except:
        num=0
    return num
class fileTokenView(APIView):
    #查询订单类型
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = UploadTokenSerializer(data=request.query_params)
        if valObj.is_valid():
            policy = {
                'callbackUrl': '{}/file/callback'.format(base_url),
                'callbackBody': 'hash=$(etag)'
            }
            result = []
            token = get_token(bucket_name=data['bucket'], policy=policy, access_key=access_key, secret_key=secret_key,
                              timeout=7200)
            post_result={
                "upload_token":token
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

class fileCallbackView(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        hash = data['hash']
        post_result = dict(resource_url='http://customer.518dh.com.cn/{}'.format(hash))
        return Response(post_result)

###################公用基础资料 ######################################
class basicView(APIView):
    #查询订单类型
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = BasicTypeSerializer(data=request.query_params)
        result = []
        if valObj.is_valid():
            bTypeObj = BasicType.objects.filter(type=data['type_name'])
            if bTypeObj.count() > 0:
                rObj = Basic.objects.filter(type_id=bTypeObj[0].id,delete_time=None).order_by('weight')
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["basic_value_en"] = one.basic_value_en
                    temp["basic_value_zh"] = one.basic_value_zh
                    temp['id'] = one.id
                    temp['weight'] = one.weight
                    result.append(temp)
            return Response(result)
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
    #添加用料单位
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = BasicInsertSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = BasicInsertSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        result = []
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                bTypeObj = BasicType.objects.filter(type=done['type_name'])
                if bTypeObj.count()>0:
                    try:
                        num = Basic.objects.all().count()+1
                        mid = done["id"]
                        if mid:
                            bObj = Basic.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = Basic()
                            bObj.create_time = dt
                        bObj.basic_value_en = done['basic_value_en']
                        bObj.basic_value_zh = done['basic_value_zh']
                        bObj.active = done['active']
                        bObj.type_id = bTypeObj[0].id
                        if not mid:
                            bObj.weight = num
                        bObj.save()
                    except:
                        msg = "参数校验不通过！"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
            msg = "添加基础资料成功"
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
                bObj = Basic.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "样品分类删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "样品分类不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class basicUpdateView(APIView):
    #订单类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = BasicTypeUpdateSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Basic.objects.get(id=nid)
            bObj.active = data['active']
            if data['basic_value_en']:
                bObj.basic_value_en = data['basic_value_en']
            if data['basic_value_zh']:
                bObj.basic_value_zh = data['basic_value_zh']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "基础资料更新成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Basic.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "基础资料不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class basicSortView(APIView):
    #基础资料排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = Basic.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = Basic.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "基础资料排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################样品类型###############################################
class sampleTypeView(APIView):
    # 样品类型名称
    @csrf_exempt
    def get(self, request):
        result = []
        try:
            rObj = SampleType.objects.filter(delete_time=None).order_by('weight')
            for one in rObj:
                temp = {}
                if one.active == 1:
                    temp['active'] = True
                else:
                    temp['active'] = False
                if one.balance == 1:
                    temp['balance'] = True
                else:
                    temp['balance'] = False
                temp["sample_type_en"] = one.sample_type_en
                temp["sample_type_zh"] = one.sample_type_zh
                temp['id'] = one.id
                temp['weight'] = one.weight
                result.append(temp)
            return Response(result)
        except:
            msg = "未找到样品类型名称"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 添加样品类型
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = SampleInsertSerializer(data=request.query_params)
        result = []
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = SampleInsertSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = SampleType.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = SampleType()
                        bObj.create_time = dt
                    num = SampleType.objects.all().count() + 1

                    bObj.sample_type_zh = done['sample_type_zh']
                    bObj.sample_type_en = done['sample_type_en']
                    bObj.active = done['active']
                    bObj.balance = done['balance']
                    if not mid:
                        bObj.weight = num
                    bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "创建样品类型成功"
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
                bObj = SampleType.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "样品分类删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "样品分类不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)

class sampleOneView(APIView):
    #样品类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = SampleInsertSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = SampleType.objects.get(id=nid)
            bObj.active = data['active']
            bObj.balance = data['balance']
            bObj.sample_type_en = data['sample_type_en']
            bObj.sample_type_zh = data['sample_type_zh']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新样品类型成功!",
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
    #删除样品类型
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = SampleType.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "样品类型删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "样品类型不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class sampleSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = SampleType.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = SampleType.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "样品分类排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################起运港###############################################
class harbourView(APIView):
    # 起运港/目的港
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = harborSerializer(data=request.query_params)
        result = []
        if valObj.is_valid():
            result = []
            try:
                rObj = Harbour.objects.filter(harbour_type=data["harbour_type"],delete_time=None).order_by('weight')
                if rObj.count()>0:
                    for one in rObj:
                        bObj = Basic.objects.get(id=one.order_id)
                        temp = {}
                        if one.active == 1:
                            temp['active'] = True
                        else:
                            temp['active'] = False
                        temp["harbour_en"] = one.harbour_en
                        temp["harbour_zh"] = one.harbour_zh
                        temp['order_id'] = one.order_id
                        temp['harbour_id'] = one.id
                        temp['basic_value_zh'] = bObj.basic_value_zh
                        temp['weight'] = one.weight
                        result.append(temp)
                    return Response(result)
                else:
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": 1,
                        "data": [],
                        "request": request
                    }
                    return Response(post_result)
            except:
                msg = "未找到对应的起运港"
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

    # 添加起运港/目的港
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = harborOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = harborOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = Harbour.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.harbour_zh = done['harbour_zh']
                        bObj.harbour_en = done['harbour_en']
                        bObj.harbour_type = done['harbour_type']
                        bObj.active = done['active']
                        bObj.order_id = done['order_id']
                        bObj.save()
                    else:
                        harbour = Harbour.objects.filter(
                            harbour_zh=done['harbour_zh'],
                            order_id=done['order_id'],
                            harbour_type=done['harbour_type'],
                            delete_time=None
                        )
                        if harbour.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "港口信息已经存在"
                            samp['key_num'] = done['harbour_zh']
                            l_msg.append(samp)
                        else:
                            bObj = Harbour()
                            bObj.create_time = dt
                            num = Harbour.objects.all().count() + 1
                            bObj.harbour_zh = done['harbour_zh']
                            bObj.harbour_en = done['harbour_en']
                            bObj.harbour_type = done['harbour_type']
                            bObj.active = done['active']
                            bObj.order_id = done['order_id']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建港口信息"
                error_code = 0
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
                bObj = Harbour.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "样品分类删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "样品分类不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)

class houbourOneView(APIView):
    #起运港-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = harborOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Harbour.objects.get(id=nid)
            bObj.active = data['active']
            bObj.harbour_en = data['harbour_en']
            bObj.harbour_zh = data['harbour_zh']
            bObj.harbour_type = data['harbour_type']
            bObj.order_id = data['order_id']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新起运港成功!",
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
    #删除起运港
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Harbour.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "起运港删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "起运港不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class harbourSortView(APIView):
    #起运港排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = Harbour.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = Harbour.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "起运港排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################商品尺码###############################################
class sizeView(APIView):
    @csrf_exempt
    def get(self, request):
        result = []
        data = request.query_params
        valObj = goodsSizeSerializer(data=request.query_params)
        result = []
        if valObj.is_valid():
            rObj = GoodsSize.objects.filter(delete_time=None).order_by('weight')
            for one in rObj:
                temp = {}
                if one.active == 1:
                    temp['active'] = True
                else:
                    temp['active'] = False
                temp["goods_size"] = one.goods_size
                temp["id"] = one.id
                subObj = []
                subAll = Size.objects.filter(goods_size_id=one.id, delete_time=None)
                for o in subAll:
                    samp = { }
                    if o.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    samp['goods_size_id'] = o.goods_size_id
                    samp['id'] = o.id
                    samp['size'] = o.size
                    samp['weight'] = o.weight
                    subObj.append(samp)
                temp['sub_size'] = subObj
                temp['weight'] = one.weight
                result.append(temp)
            return Response(result)
        else:
            msg = "未找到商品尺码名称"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 添加商品尺码
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = sizeOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = sizeOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = GoodsSize.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.goods_size = done['goods_size']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        goods_size = GoodsSize.objects.filter(
                            goods_size=done['goods_size'],
                            delete_time=None
                        )
                        if goods_size.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "商品尺码已经存在"
                            samp['key_num'] = done['goods_size']
                            l_msg.append(samp)
                        else:
                            bObj = GoodsSize()
                            bObj.create_time = dt
                            num = GoodsSize.objects.all().count() + 1
                            bObj.goods_size = done['goods_size']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建商品尺码"
                error_code = 0
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
                bObj = GoodsSize.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "尺码删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "尺码不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class sizeOneView(APIView):
    #订单类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = sizeOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = GoodsSize.objects.get(id=nid)
            bObj.active = data['active']
            bObj.goods_size = data['goods_size']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新商品尺码成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = GoodsSize.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "商品尺码删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "商品尺码不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class sizeSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = GoodsSize.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = GoodsSize.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": " 商品尺码排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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


############################商品子尺码###############################################
class subsizeView(APIView):
    # 添加商品子尺码
    @csrf_exempt
    def post(self, request):
        data = request.query_params
        valObj = subsizeOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = subsizeOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = Size.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.size = done['size']
                        bObj.goods_size_id = done['goods_size_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        size = Size.objects.filter(
                            goods_size_id=done['goods_size_id'],
                            size=done['size'],
                            delete_time=None
                        )
                        if size.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "商品子尺码已经存在"
                            samp['key_num'] = done['size']
                            l_msg.append(samp)
                        else:
                            bObj = Size()
                            bObj.create_time = dt
                            num = Size.objects.all().count() + 1
                            bObj.size = done['size']
                            bObj.goods_size_id = done['goods_size_id']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建商品子尺码"
                error_code = 0
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
                bObj = Size.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "子尺码删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "子尺码不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)

class subsizeOneView(APIView):

    # 获取子尺码
    @csrf_exempt
    def get(self, request, nid):
        result = []
        try:
            rObj = Size.objects.filter(goods_size_id=nid, delete_time=None).order_by('weight')
            for one in rObj:
                temp = {}
                if one.active == 1:
                    temp['active'] = True
                else:
                    temp['active'] = False
                goods_size_obj = GoodsSize.objects.get(id = one.goods_size_id)
                temp["goods_size"] = goods_size_obj.goods_size
                temp["goods_size_id"] = one.goods_size_id
                temp['size_id'] = one.id
                temp["size"] = one.size
                temp['weight'] = one.weight
                result.append(temp)
            return Response(result)
        except:
            msg = "未找到商品子尺码"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #子尺码更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = subsizeOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Size.objects.get(id=nid)
            bObj.active = data['active']
            bObj.goods_size = data['goods_size']
            bObj.size = data['size']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新商品子尺码成功!",
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

    #删除子尺码
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Size.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "商品子尺码删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "商品子尺码不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class subsizeSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = Size.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = Size.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": " 商品子尺码排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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


############################ 收货方式###############################################
class receivingView(APIView):
    @csrf_exempt
    def get(self, request):
        result = []
        try:
            rObj = ReceivingGoodsMethod.objects.filter(delete_time=None).order_by('weight')
            for one in rObj:
                temp = {}
                if one.active == 1:
                    temp['active'] = True
                else:
                    temp['active'] = False
                temp["method_name"] = one.method_name
                temp["id"] = one.id
                subObj = []
                subAll = WarehouseClassification.objects.filter(method_id=one.id, delete_time=None)
                for o in subAll:
                    samp =  {}
                    if o.active == 1:
                        samp['active'] = True
                    else:
                        samp['active'] = False
                    samp['method_id'] = o.method_id
                    samp['id'] = o.id
                    samp['warehouse_name'] = o.warehouse_name
                    samp['weight'] = o.weight
                    subObj.append(samp)
                temp['warehouse'] = subObj
                temp['weight'] = one.weight
                result.append(temp)
            return Response(result)
        except:
            msg = "未找到收货方式"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 添加收货方式
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = receivingOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = receivingOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = ReceivingGoodsMethod.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.method_name = done['method_name']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        receiObj = ReceivingGoodsMethod.objects.filter(
                            method_name=done['method_name'],
                            delete_time=None
                        )
                        if receiObj.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "收货已经存在"
                            samp['key_num'] = done['method_name']
                            l_msg.append(samp)
                        else:
                            bObj = ReceivingGoodsMethod()
                            bObj.create_time = dt
                            num = ReceivingGoodsMethod.objects.all().count() + 1
                            bObj.method_name = done['method_name']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag ==0:
                msg = "创建收货方式"
                error_code = 0
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
                bObj = ReceivingGoodsMethod.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "收货方式删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "收货方式不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class receivingOneView(APIView):
    # 收货方式-更新
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = receivingOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ReceivingGoodsMethod.objects.get(id=nid)
            bObj.active = data['active']
            bObj.method_name = data['method_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新收货方式成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ReceivingGoodsMethod.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "收货方式删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = " 收货方式不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class receivingSortView(APIView):
    # 收货方式排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ReceivingGoodsMethod.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ReceivingGoodsMethod.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "收货方式排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################ 子仓库###############################################
class warehouseView(APIView):
    # 添加商品子尺码
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = warehouseSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = warehouseSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = WarehouseClassification.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.warehouse_name = done['warehouse_name']
                        bObj.method_id = done['method_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        whouse = WarehouseClassification.objects.filter(
                            warehouse_name=done['warehouse_name'],
                            method_id=done['method_id'],
                            delete_time=None
                        )
                        if whouse.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "子仓库已经存在"
                            samp['key_num'] = done['warehouse_name']
                            l_msg.append(samp)
                        else:
                            bObj = WarehouseClassification()
                            bObj.create_time = dt
                            num = WarehouseClassification.objects.all().count() + 1
                            bObj.warehouse_name = done['warehouse_name']
                            bObj.method_id = done['method_id']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag==0:
                msg = "创建/更新子仓库"
                error_code = 0
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
                bObj = WarehouseClassification.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "子仓库删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "子仓库不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class warehouseOneView(APIView):

    # 获取子尺码
    @csrf_exempt
    def get(self, request, nid):
        result = []
        try:
            rObj = WarehouseClassification.objects.filter(method_id=nid, delete_time=None).order_by('weight')
            for one in rObj:
                temp = {}
                if one.active == 1:
                    temp['active'] = True
                else:
                    temp['active'] = False
                w_obj = ReceivingGoodsMethod.objects.get(id = one.method_id)
                temp["method_id"] = one.method_id
                temp["id"] = one.id
                temp['warehouse_name'] = one.warehouse_name
                temp["method_name"] = w_obj.method_name
                temp['weight'] = one.weight
                result.append(temp)
            return Response(result)
        except:
            msg = "未找到子仓库"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #子尺码更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = warehouseSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = WarehouseClassification.objects.get(id=nid)
            bObj.active = data['active']
            bObj.warehouse_name = data['warehouse_name']
            bObj.method_id = data['method_id']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新商品子尺码成功!",
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

    #删除子仓库
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = WarehouseClassification.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "商品子尺码删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "商品子尺码不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class warehouseSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = WarehouseClassification.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = WarehouseClassification.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": " 子仓库排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################ 订单号设置###############################################
class singlesetView(APIView):
    # 查询订单号
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = singleSetSerializer(data=request.query_params)
        result = []
        if valObj.is_valid():
            bTypeObj = BasicType.objects.filter(type=data['type_name'])
            if bTypeObj.count() > 0:
                rObj = SingleSet.objects.filter(type_id=bTypeObj[0].id, delete_time=None)
                for one in rObj:
                    temp = {}
                    temp["code_number_start"] = one.code_number_start
                    temp["code_sign_start"] = one.code_sign_start
                    temp['id'] = one.id
                    temp['customer_type_id'] = one.customer_type_id
                    sObj = CustomerType.objects.filter(id= one.customer_type_id)
                    if sObj.count()>0:
                        temp['customer_type'] = sObj[0].customer_type
                    temp['prefix_name'] = one.prefix_name
                    temp['time_type'] = one.time_type
                    result.append(temp)
            return Response(result)
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

    # 添加 订单号设置
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = singleSetOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = singleSetOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    btObj = BasicType.objects.filter(type=done['type_name'])
                    if btObj.count() > 0:
                        mid = done["id"]
                        if mid:
                            bObj = SingleSet.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = SingleSet()
                            bObj.create_time = dt
                        bObj.customer_type_id = done['customer_type_id']
                        bObj.prefix_name = done['prefix_name']
                        bObj.time_type = done['time_type']
                        bObj.code_sign_start = done['code_sign_start']
                        bObj.code_number_start = done['code_number_start']
                        cObj = CustomerType.objects.filter(id=done['customer_type_id'])
                        if cObj.count()>0:
                            cObj[0].seleted_single = 1
                            cObj[0].seleted_invoice = 0
                            cObj[0].update_time = dt
                            cObj[0].save()
                        bObj.type_id = btObj[0].id
                        bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "创建/更新订单号"
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
                bObj = SingleSet.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "设置信息删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "设置信息不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class singlesetOneView(APIView):
    #订单号更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = singleSetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = SingleSet.objects.filter(id=nid)
            if bObj.count()>0:
                bObj = bObj[0]
            else:
                post_result = {
                    "error_code": 10020,
                    "message": "设置信息不存在!",
                    "request": request,
                }
                return Response(post_result)
            bObj.prefix_name = data['prefix_name']
            bObj.time_type = data['time_type']
            bObj.code_sign_start = data['code_sign_start']
            bObj.code_number_start = data['code_number_start']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新订单号成功!",
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

    #删除 订单号
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = SingleSet.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "设置信息删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "设置信息不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################  发票号设置###############################################
class invoiceView(APIView):
    # 查询 发票号
    @csrf_exempt
    def get(self, request):
        result = []
        try:
            bTypeObj = InvoiceSetting.objects.filter(delete_time=None)
            for one in bTypeObj:
                temp = {}
                temp["code_number_start"] = one.code_number_start
                temp["prefix_name"] = one.prefix_name
                temp['id'] = one.id
                temp['prefix_type'] = one.prefix_type
                result.append(temp)
            return Response(result)
        except:
            msg = "未找到发票号信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 添加  发票号
    @csrf_exempt
    def post(self, request):
        data = request.query_params
        valObj = invoiceSerializer(data=request.query_params)
        dt = datetime.now()
        if valObj.is_valid():
            try:
                btObj = InvoiceSetting.objects.all()
                if btObj.count() > 0:
                    msg = "只能存在一条信息！"
                    error_code = 413
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
                else:
                    bObj = InvoiceSetting()
                    bObj.prefix_type = data['prefix_type']
                    bObj.prefix_name = data['prefix_name']
                    bObj.code_number_start = data['code_number_start']
                    bObj.create_time = dt
                    bObj.save()
                    msg = "创建发票号"
                    error_code = 0
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            except:
                msg = "参数校验不通过！"
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

class invoiceOneView(APIView):
    # 发票号更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = invoiceSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = InvoiceSetting.objects.filter(id=nid)
            if bObj.count()>0:
                bObj = bObj[0]
            else:
                post_result = {
                    "error_code": 10020,
                    "message": "设置信息不存在!",
                    "request": request,
                }
                return Response(post_result)
            bObj.prefix_type = data['prefix_type']
            bObj.prefix_name = data['prefix_name']
            bObj.code_number_start = data['code_number_start']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新发票号成功!",
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


############################面辅料类别###############################################
class cloth_classView(APIView):
    # 面辅料类别
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = cloth_classSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = ClothClass.objects.filter(delete_time=None).order_by('weight')
                active = valObj.data['active'] if valObj.data['active'] is not None else 2
                cloth_class_name = valObj.data['cloth_class_name'] if valObj.data['cloth_class_name'] is not None else ''
                if active !=2:
                    rObj = rObj.filter(active = active)
                if cloth_class_name:
                    rObj = rObj.filter(cloth_class_name__contains=cloth_class_name)
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["cloth_class_name"] = one.cloth_class_name
                    temp["id"] = one.id
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的面辅料类别"
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

    # 添加面辅料类别
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = cloth_classOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = cloth_classOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = ClothClass.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.cloth_class_name = done['cloth_class_name']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        clothClass = ClothClass.objects.filter(
                            cloth_class_name=done['cloth_class_name'],
                            delete_time=None
                        )
                        if clothClass.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "面辅料分类已经存在"
                            samp['key_num'] = done['cloth_class_name']
                            l_msg.append(samp)
                        else:
                            bObj = ClothClass()
                            bObj.create_time = dt
                            num = ClothClass.objects.all().count() + 1
                            bObj.cloth_class_name = done['cloth_class_name']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()

                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag==0:
                msg = "创建/更新面料分类"
                error_code = 0
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
                bObj = ClothClass.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料类别不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class cloth_classOneView(APIView):
    # 面辅料类别更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = cloth_classOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ClothClass.objects.get(id=nid)
            bObj.active = data['active']
            bObj.cloth_class_name = data['cloth_class_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新面辅料类别成功!",
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
    #删除 面辅料类别
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ClothClass.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面料分类删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面料分类不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class cloth_classSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ClothClass.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ClothClass.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "面辅料类别排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################面辅料成分###############################################
class clothmaterialView(APIView):
    # 添加面辅料成分
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = clothMaterialOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = clothMaterialOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    clothM = ClothMaterial.objects.filter(
                        material=done['material'],
                        cloth_id=done['cloth_id'],
                        delete_time=None
                    )
                    if clothM.count()>0:
                        d_flag = 1
                        samp = {}
                        samp['msg'] = "面辅料材料已经存在"
                        samp['key_num'] = done['material']
                        l_msg.append(samp)
                    else:
                        mid = done["id"]
                        if mid:
                            bObj = ClothMaterial.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = ClothMaterial()
                            bObj.create_time = dt
                        num = ClothMaterial.objects.all().count() + 1
                        bObj.material = done['material']
                        bObj.active = done['active']
                        bObj.cloth_id = done['cloth_id']
                        bObj.create_time = dt
                        if not mid:
                            bObj.weight = num
                        bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建/更新面料材料"
                error_code = 0
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
                bObj = ClothMaterial.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料成分删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料成分不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class clothmaterialOneView(APIView):
    # 面辅料类别
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        cloth = Cloth.objects.filter(id=nid,delete_time=None)
        if cloth.count()>0:
            result = []
            try:
                rObj = ClothMaterial.objects.filter(cloth_id=nid,delete_time=None).order_by('weight')
                for one in rObj:
                    ccobj = ClothClass.objects.filter(id=cloth[0].class_id,delete_time=None)
                    if ccobj.count()>0:
                        temp = {}
                        if one.active == 1:
                            temp['active'] = True
                        else:
                            temp['active'] = False
                        temp["class_id"] = cloth[0].class_id
                        temp["cloth_class_name"] = ccobj[0].cloth_class_name
                        temp["cloth_id"] = one.cloth_id
                        temp["cloth_name"] = cloth[0].cloth
                        temp["material"] = one.material
                        temp["material_id"] = one.id
                        temp['weight'] = one.weight
                        result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的面辅料信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = "未找到对应的面辅料信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 面辅料类别更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = clothMaterialUOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ClothMaterial.objects.get(id=nid)
            bObj.active = data['active']
            bObj.material = data['material']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新面辅料成功!",
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
    #删除 面辅料类别
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ClothMaterial.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面料分类删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面料分类不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class clothmaterialSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ClothMaterial.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ClothMaterial.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "面辅料排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################面辅料名称###############################################
class clothView(APIView):
    # 面辅料名称
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = clothSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = Cloth.objects.filter(delete_time=None).order_by('weight')
                class_id = valObj.data['class_id'] if valObj.data['class_id'] is not None else 0
                cloth = valObj.data['cloth'] if valObj.data['cloth'] is not None else ''
                if class_id:
                    rObj = rObj.filter(class_id = class_id)
                if cloth:
                    rObj = rObj.filter(cloth__contains=cloth)
                for one in rObj:
                    ccobj = ClothClass.objects.filter(id=one.class_id,delete_time=None)
                    if ccobj.count()>0:
                        temp = {}
                        if one.active == 1:
                            temp['active'] = True
                        else:
                            temp['active'] = False
                        if one.checked == 1:
                            temp['checked'] = True
                        else:
                            temp['checked'] = False
                        temp["cloth"] = one.cloth
                        temp["cloth_class_name"] = ccobj[0].cloth_class_name
                        temp["cloth_id"] = one.id
                        cmobj = ClothMaterial.objects.filter(cloth_id= one.id,delete_time=None)
                        samp=[]
                        for o in cmobj:
                            sampd={}
                            sampd['class_id'] = one.class_id
                            if o.active == 1:
                                sampd['active'] = True
                            else:
                                sampd['active'] = False
                            sampd['cloth_class_name'] =ccobj[0].cloth_class_name
                            sampd['cloth_id'] =one.id
                            sampd['cloth_name'] = one.cloth
                            sampd['material'] = o.material
                            sampd['material_id'] = o.id
                            sampd['weight'] = o.weight
                            samp.append(sampd)
                        temp['materials'] = samp
                        temp['weight'] = one.weight
                        result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的 面辅料名称"
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

    # 添加面辅料名称
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = clothOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = clothOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = Cloth.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.cloth = done['cloth']
                        bObj.active = done['active']
                        bObj.checked = done['checked']
                        bObj.class_id = done['class_id']
                        bObj.save()
                    else:
                        cloth = Cloth.objects.filter(
                            cloth=done['cloth'],
                            class_id=done['class_id'],
                            delete_time=None
                        )
                        if cloth.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "面料名称已经存在"
                            samp['key_num'] = done['cloth']
                            l_msg.append(samp)
                        else:
                            bObj = Cloth()
                            bObj.create_time = dt
                            num = Cloth.objects.all().count() + 1
                            bObj.cloth = done['cloth']
                            bObj.active = done['active']
                            bObj.checked = done['checked']
                            bObj.class_id = done['class_id']
                            bObj.weight = num
                            bObj.save()

                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建面料"
                error_code = 0
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
                bObj = Cloth.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料名称删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料名称不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class clothOneView(APIView):
    # 面辅料类别更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = clothOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Cloth.objects.get(id=nid)
            bObj.active = data['active']
            bObj.checked = data['checked']
            bObj.class_id = data['class_id']
            bObj.cloth = data['cloth']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新面辅料成功!",
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
    #删除 面辅料
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Cloth.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面料删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面料分类不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class clothSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = Cloth.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = Cloth.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "面辅料排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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


############################面辅料颜色###############################################
class colourView(APIView):
    # 面辅料颜色
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = colourSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = ClothColour.objects.filter(delete_time=None).order_by('weight')
                colour_name = valObj.data['colour_name'] if valObj.data['colour_name'] is not None else ''
                if colour_name:
                    rObj = rObj.filter(colour_name__contains=colour_name)
                for one in rObj:

                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["colour_name"] = one.colour_name
                    temp["id"] = one.id
                    ccsobj = SubColour.objects.filter(colour_id=one.id, delete_time=None)
                    samp=[]
                    for o in ccsobj:
                        sampd={}
                        if o.active == 1:
                            sampd['active'] = True
                        else:
                            sampd['active'] = False
                        sampd['colour_id'] =o.id
                        sampd['id'] =one.id
                        sampd['sub_colour_name'] = o.sub_colour_name
                        sampd['weight'] = o.weight
                        samp.append(sampd)
                    temp['sub_colour'] = samp
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的 面辅料颜色"
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

    # 添加面辅料名称
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = colourOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = colourOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = ClothColour.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.colour_name = done['colour_name']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        colour = ClothColour.objects.filter(
                            colour_name=done['colour_name'],
                            delete_time=None
                        )
                        if colour.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "面料颜色已经存在"
                            samp['key_num'] = done['colour_name']
                            l_msg.append(samp)
                        else:
                            bObj = ClothColour()
                            bObj.create_time = dt
                            num = ClothColour.objects.all().count() + 1
                            bObj.colour_name = done['colour_name']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()

                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建/更新面料颜色"
                error_code = 0
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
                bObj = ClothColour.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料颜色删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料颜色不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class colourOneView(APIView):
    # 面辅料类别更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = colourOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ClothColour.objects.get(id=nid)
            bObj.active = data['active']
            bObj.colour_name = data['colour_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新面辅料颜色成功!",
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
    #删除 面辅料
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ClothColour.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面料颜色删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面料颜色不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class colourSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ClothColour.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ClothColour.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "面辅料颜色排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################面辅料子颜色###############################################
class sub_colourView(APIView):
    # 添加面辅料子颜色
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = subcolourOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = subcolourOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = SubColour.objects.get(id=mid)
                        bObj.update_time = dt

                        bObj.sub_colour_name = done['sub_colour_name']
                        bObj.active = done['active']
                        bObj.colour_id = done['colour_id']

                        bObj.save()
                    else:
                        scol = SubColour.objects.filter(
                            sub_colour_name=done['sub_colour_name'],
                            colour_id=done['colour_id'],
                            delete_time=None
                        )
                        if scol.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "子颜色已经存在"
                            samp['key_num'] = done['sub_colour_name']
                            l_msg.append(samp)
                        else:
                            bObj = SubColour()
                            bObj.create_time = dt
                            num = SubColour.objects.all().count() + 1
                            bObj.sub_colour_name = done['sub_colour_name']
                            bObj.active = done['active']
                            bObj.colour_id = done['colour_id']
                            if not mid:
                                bObj.weight = num
                            bObj.save()


                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建面料子颜色"
                error_code = 0
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
                bObj = SubColour.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料子颜色删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料子颜色不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class sub_colourOneView(APIView):
    # 面辅料子颜色
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        cloth = ClothColour.objects.filter(id=nid,delete_time=None)
        if cloth.count()>0:
            result = []
            try:
                rObj = SubColour.objects.filter(colour_id=nid,delete_time=None).order_by('weight')
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["colour_id"] = one.colour_id
                    temp["sub_colour_name"] = one.sub_colour_name
                    temp["colour_name"] = cloth[0].colour_name
                    temp['id'] = one.id
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的面辅料信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = "未找到对应的面辅料信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 面辅料子颜色更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = subcolourUOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = SubColour.objects.get(id=nid)
            bObj.active = data['active']
            bObj.sub_colour_name = data['sub_colour_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新面辅料子颜色成功!",
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
    #删除 面辅料子颜色
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = SubColour.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料子颜色删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面料分类不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class sub_colourSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = SubColour.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ClothMaterial.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "面辅料排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################ 面辅料规格###############################################
class specsView(APIView):
    # 面辅料规格
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = specsSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = ClothSpecs.objects.filter(delete_time=None).order_by('weight')
                specs_name = valObj.data['specs_name'] if valObj.data['specs_name'] is not None else ''
                if specs_name:
                    rObj = rObj.filter(specs_name__contains=specs_name)
                for one in rObj:

                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["specs_name"] = one.specs_name
                    temp["specs_unit"] = one.specs_unit
                    temp["id"] = one.id
                    sub_specs = SubSpecs.objects.filter(specs_id=one.id, delete_time=None)
                    samp=[]
                    for o in sub_specs:
                        sampd={}
                        if o.active == 1:
                            sampd['active'] = True
                        else:
                            sampd['active'] = False
                        sampd['specs_id'] =one.id
                        sampd['id'] =o.id
                        sampd['sub_specs_name'] = o.sub_specs_name
                        sampd['weight'] = o.weight
                        samp.append(sampd)
                    temp['sub_specs'] = samp
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的 面辅料规格"
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

    # 面辅料规格
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = specsOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = specsOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:

                    mid = done["id"]
                    if mid:
                        bObj = ClothSpecs.objects.get(id=mid)
                        bObj.update_time = dt

                        bObj.specs_name = done['specs_name']
                        bObj.specs_unit = done['specs_unit']
                        bObj.active = done['active']

                        bObj.save()
                    else:
                        specs = ClothSpecs.objects.filter(
                            specs_name=done['specs_name'],
                            delete_time=None
                        )
                        if specs.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "面辅料规格已经存在"
                            samp['key_num'] = done['specs_name']
                            l_msg.append(samp)
                        else:
                            bObj = ClothSpecs()
                            bObj.create_time = dt
                            num = ClothSpecs.objects.all().count() + 1
                            bObj.specs_name = done['specs_name']
                            bObj.specs_unit = done['specs_unit']
                            bObj.active = done['active']

                            bObj.weight = num
                            bObj.save()

                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建面料规格"
                error_code = 0
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
                bObj = ClothSpecs.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料规格删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料规格不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class specsOneView(APIView):
    # 面辅料类别更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = specsOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ClothSpecs.objects.get(id=nid)
            bObj.active = data['active']
            bObj.specs_name = data['specs_name']
            bObj.specs_unit = data['specs_unit']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新面辅料规格成功!",
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
    #删除 面辅料
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ClothSpecs.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面料规格删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面料规格不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class specsSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ClothSpecs.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ClothSpecs.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "面辅料规格排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################ 面辅料子规格###############################################
class sub_specsView(APIView):
    # 面辅料子规格
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = subspecsSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = subspecsSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = SubSpecs.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.sub_specs_name = done['sub_specs_name']
                        bObj.active = done['active']
                        bObj.specs_id = done['specs_id']
                        bObj.save()

                    else:
                        sspecs = SubSpecs.objects.filter(
                            sub_specs_name=done['sub_specs_name'],
                            specs_id=done['specs_id'],
                            delete_time=None
                        )
                        if sspecs.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "子规格已经存在"
                            samp['key_num'] = done['sub_specs_name']
                            l_msg.append(samp)
                        else:
                            bObj = SubSpecs()
                            bObj.create_time = dt
                            num = SubSpecs.objects.all().count() + 1
                            bObj.sub_specs_name = done['sub_specs_name']
                            bObj.active = done['active']
                            bObj.specs_id = done['specs_id']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建面料子规格"
                error_code = 0
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
                bObj = SubSpecs.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料子规格删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面辅料子规格不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)



class sub_specsOneView(APIView):
    # 面辅料子规格
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        cloth = ClothSpecs.objects.filter(id=nid,delete_time=None)
        if cloth.count()>0:
            result = []
            try:
                rObj = SubSpecs.objects.filter(specs_id=nid,delete_time=None).order_by('weight')
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["specs_id"] = one.specs_id
                    temp["sub_specs_name"] = one.sub_specs_name
                    temp["specs_name"] = cloth[0].specs_name
                    temp["specs_unit"] = cloth[0].specs_unit
                    temp['id'] = one.id
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的面辅料信息"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = "未找到对应的面辅料信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 面辅料子规格更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = subspecsUSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = SubSpecs.objects.get(id=nid)
            bObj.active = data['active']
            bObj.sub_specs_name = data['sub_specs_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新面辅料子规格成功!",
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
    #删除 面辅料子规格
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = SubSpecs.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "面辅料子规格删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "面料子规格不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class sub_specsSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = SubSpecs.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = SubSpecs.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "面辅料子规格排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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



#*******************************客户管理****************************************************
############################客户类型设置###############################################
class customerTypeView(APIView):
    # 客户类型名称
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = customerTypeSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = CustomerType.objects.filter(delete_time=None).order_by('weight')
                if valObj.data['active'] !=2:
                    rObj = rObj.filter(active = data['active'])
                if valObj.data['selected_single'] !=2:
                    rObj = rObj.filter(selected_single = data['selected_single'])
                if valObj.data['selected_invoice'] !=2:
                    rObj = rObj.filter(selected_invoice = data['selected_invoice'])
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["customer_type"] = one.customer_type
                    temp["selected_invoice"] = one.selected_invoice
                    temp['id'] = one.id
                    temp['selected_single'] = one.selected_single
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的客户类型"
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

    # 添加客户类型
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = customerOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = customerOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = CustomerType.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.customer_type = done['customer_type']
                        bObj.active = done['active']
                        bObj.selected_single = 0
                        bObj.selected_invoice = 0
                        bObj.save()
                    else:
                        customerT = CustomerType.objects.filter(
                            customer_type=done['customer_type'],
                            delete_time=None
                        )
                        if customerT.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "客户类型已经存在"
                            samp['key_num'] = done['customer_type']
                            l_msg.append(samp)
                        else:
                            bObj = CustomerType()
                            bObj.create_time = dt
                            num = CustomerType.objects.all().count() + 1
                            bObj.customer_type = done['customer_type']
                            bObj.active = done['active']
                            bObj.selected_single = 0
                            bObj.selected_invoice = 0
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag ==0:
                msg = "创建客户类型"
                error_code = 0
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
                bObj = CustomerType.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "客户类型删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "客户类型不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class customerTypeOneView(APIView):
    #客户类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = customerOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = CustomerType.objects.get(id=nid)
            bObj.active = data['active']
            bObj.customer_type = data['customer_type']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新客户类型成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = CustomerType.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "客户类型删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "客户类型不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class customerTypeSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = CustomerType.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = CustomerType.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "客户类型排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################客户档案设置###############################################
class customer_filesView(APIView):
    # 客户档案
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = customer_filesSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                customer_simple_name = valObj.data['customer_simple_name'] if valObj.data['customer_simple_name'] is not None else ""
                order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                active = valObj.data['active'] if valObj.data['active'] is not None else 2
                if order_type==1:
                    rObj = CustomerFiles.objects.filter(delete_time=None).order_by("type_id")
                elif order_type==2:
                    rObj = CustomerFiles.objects.filter(delete_time=None).order_by("create_time")
                else:
                    rObj = CustomerFiles.objects.filter(delete_time=None)

                if data['type_id'] !='0':
                    rObj = rObj.filter(type_id=data['type_id'])

                if customer_simple_name:
                    rObj = rObj.filter(customer_simple_name__contain=customer_simple_name)
                if active != '2':
                    rObj = rObj.filter(active=active)

                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["customer_full_name"] = one.customer_full_name
                    temp["customer_simple_name"] = one.customer_simple_name
                    obj = CustomerType.objects.filter(id = one.type_id)
                    if obj.count()>0:
                        temp["customer_type"] = obj[0].customer_type
                    temp["fax_number"] = one.fax_number
                    temp['id'] = one.id
                    temp['office_phone'] = one.office_phone
                    temp['type_id'] = one.type_id
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的客户"
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

    # 添加客户档案
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = customer_filesOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = customer_filesOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = CustomerFiles.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.customer_full_name = done['customer_full_name']
                        bObj.active = done['active']
                        bObj.customer_simple_name = done['customer_simple_name']
                        bObj.office_phone = done['office_phone']
                        bObj.fax_number = done['fax_number']
                        bObj.type_id = done['type_id']
                        bObj.save()
                    else:
                        customerT = CustomerFiles.objects.filter(
                            type_id=done['type_id'],
                            customer_full_name=done['customer_full_name'],
                            delete_time=None
                        )
                        if customerT.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "客户档案已经存在"
                            samp['key_num'] = done['customer_full_name']
                            l_msg.append(samp)
                        else:
                            bObj = CustomerFiles()
                            bObj.create_time = dt
                            bObj.customer_full_name = done['customer_full_name']
                            bObj.active = done['active']
                            bObj.customer_simple_name = done['customer_simple_name']
                            bObj.office_phone = done['office_phone']
                            bObj.fax_number = done['fax_number']
                            bObj.type_id = done['type_id']
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建客户档案"
                error_code = 0
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
                bObj = CustomerFiles.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "客户档案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "客户档案不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class customer_filesOneView(APIView):
    #客户类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = customer_filesOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = CustomerFiles.objects.get(id=nid)
            bObj.active = data['active']
            bObj.customer_full_name = data['customer_full_name']
            bObj.customer_simple_name = data['customer_simple_name']
            bObj.type_id = data['type_id']
            bObj.fax_number = data['fax_number']
            bObj.office_phone = data['office_phone']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新客户档案成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = CustomerFiles.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "客户档案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "客户类型不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################ 联系方式###############################################
class contactView(APIView):
    # 添加联系方式
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = contactOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = contactOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = CustomerContact.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.customer_id = done['customer_id']
                        bObj.active = done['active']
                        bObj.department_name = done['department_name']
                        bObj.post_name = done['post_name']
                        bObj.contact_name = done['contact_name']
                        bObj.phone = done['phone']
                        bObj.email = done['email']
                        bObj.remarks = done['remarks']
                        bObj.save()
                    else:
                        customerT = CustomerContact.objects.filter(
                            customer_id=done['customer_id'],
                            department_name=done['department_name'],
                            post_name=done['post_name'],
                            contact_name=done['contact_name'],
                            phone=done['phone'],
                            email=done['email'],
                            remarks=done['remarks'],
                            delete_time=None
                        )
                        if customerT.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "联系方式已经存在"
                            samp['key_num'] = done['phone']
                            l_msg.append(samp)
                        else:
                            bObj = CustomerContact()
                            bObj.create_time = dt
                            bObj.customer_id = done['customer_id']
                            bObj.active = done['active']
                            bObj.department_name = done['department_name']
                            bObj.post_name = done['post_name']
                            bObj.contact_name = done['contact_name']
                            bObj.phone = done['phone']
                            bObj.email = done['email']
                            bObj.remarks = done['remarks']
                            bObj.save()

                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag ==0:
                msg = "创建联系方式"
                error_code = 0
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
                bObj = CustomerContact.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "联系方式删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "联系方式不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class contactOneView(APIView):
    # 联系方式
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        try:
            result = []
            try:
                rObj = CustomerContact.objects.filter(customer_id=nid, delete_time=None)
                for one in rObj:
                    temp = {}
                    temp["id"] = one.id
                    temp["contact_name"] = one.contact_name
                    temp["customer_id"] = one.customer_id
                    temp["department_name"] = one.department_name
                    temp['email'] = one.email
                    temp['phone'] = one.phone
                    temp['post_name'] = one.post_name
                    temp['remarks'] = one.remarks
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应联系方式"
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

    #客户类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = contactOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = CustomerContact.objects.get(id=nid)
            bObj.contact_id = data['contact_id']
            bObj.contact_name = data['contact_name']
            bObj.customer_id = data['customer_id']
            bObj.department_name = data['department_name']
            bObj.email = data['email']
            bObj.phone = data['phone']
            bObj.post_name = data['post_name']
            bObj.remarks = data['remarks']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新客户档案成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = CustomerContact.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "联系方式删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "联系方式不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################  公司名片###############################################
class namecardOneView(APIView):
    #  公司名片
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        try:
            result = []
            try:
                rObj = CustomerCompany.objects.filter(customer_file_id=nid, delete_time=None)
                for one in rObj:
                    temp = {}
                    temp["id"] = one.id
                    temp["company_name"] = one.company_name
                    temp["language"] = one.language
                    temp["company_name_simple"] = one.company_name_simple
                    temp['country'] = one.country
                    temp['company_address'] = one.company_address
                    temp['customer_file_id'] = one.customer_file_id
                    mobj = Marks.objects.filter(namecard_id=one.id)
                    samp = []
                    for o in mobj:
                        sampd = {}
                        if o.active == 1:
                            temp['active'] = True
                        else:
                            temp['active'] = False
                        sampd['brand'] = o.brand
                        sampd['brand_url'] = o.brand_url
                        sampd['company_name_simple'] = one.company_name_simple
                        sampd['customer_company_id'] = o.namecard_id
                        sampd['id'] = o.id
                        sampd['namecard_id'] = o.namecard_id
                        samp.append(sampd)
                    temp['marks'] = samp
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应公司名片"
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

    # 添加 公司名片
    @csrf_exempt
    def post(self, request, nid):
        # data = request.query_params
        # valObj = namecardOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = namecardOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        cfObj = CustomerFiles.objects.filter(id=nid)
        if cfObj.count()>0:
            dt = datetime.now()
            if d_flag == 0:
                for done in data:
                    try:
                        mid = done["id"]
                        if mid:
                            bObj = CustomerCompany.objects.get(id=mid)
                            bObj.update_time = dt
                            bObj.customer_file_id = nid
                            bObj.language = done['language']
                            bObj.company_name = done['company_name']
                            bObj.company_name_simple = done['company_name_simple']
                            bObj.country = done['country']
                            bObj.company_address = done['company_address']
                            bObj.save()
                        else:
                            customerT = CustomerCompany.objects.filter(
                                company_name=done['company_name'],
                                customer_file_id=nid,
                                delete_time=None
                            )
                            if customerT.count() > 0:
                                d_flag = 1
                                samp = {}
                                samp['msg'] = "客户名片已经存在"
                                samp['key_num'] = done['company_name']
                                l_msg.append(samp)
                            else:
                                bObj = CustomerCompany()
                                bObj.create_time = dt
                                bObj.customer_file_id = nid
                                bObj.language = done['language']
                                bObj.company_name = done['company_name']
                                bObj.company_name_simple = done['company_name_simple']
                                bObj.country = done['country']
                                bObj.company_address = done['company_address']
                                bObj.save()
                    except:
                        msg = "参数校验不通过！"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                if d_flag==0:
                    msg = "创建联系方式"
                    error_code = 0
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
            msg = "客户档案不存在"
            error_code = 404
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
    # 公司名片更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = namecardOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = CustomerCompany.objects.get(id=nid)
            bObj.id = nid
            bObj.language = data['language']
            bObj.company_name = data['company_name']
            bObj.company_name_simple = data['company_name_simple']
            bObj.country = data['country']
            bObj.company_address = data['company_address']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新客户名片成功!",
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
    #删除 公司名片
    @csrf_exempt
    def delete(self, request, nid):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = CustomerCompany.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "客户名片删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "客户名片不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################  唛头###############################################
class marksOneView(APIView):
    #  唛头
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        try:
            result = []
            try:
                rObj = Marks.objects.filter(namecard_id=nid, delete_time=None)
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["id"] = one.id
                    temp["brand"] = one.brand
                    temp["brand_url"] = one.brand_url
                    ccobj = CustomerCompany.objects.get(id=nid)
                    temp["company_name_simple"] = ccobj.company_name_simple
                    temp['customer_company_id'] = one.namecard_id
                    temp['namecard_id'] = one.namecard_id
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应公司唛头"
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
    # 添加 唛头
    @csrf_exempt
    def post(self, request, nid):
        # data = request.query_params
        # valObj = marksOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = marksOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        cfObj = CustomerCompany.objects.filter(id=nid)
        if cfObj.count()>0:
            dt = datetime.now()
            if d_flag == 0:
                for done in data:
                    try:
                        mid = done["id"]
                        if mid:
                            bObj = Marks.objects.get(id=mid)
                            bObj.update_time = dt
                            bObj.namecard_id = done['namecard_id']
                            bObj.brand = done['brand']
                            bObj.brand_url = done['brand_url']
                            bObj.active = done['active']
                            bObj.save()
                        else:
                            customerT = Marks.objects.filter(
                                namecard_id=done['namecard_id'],
                                brand=done['brand'],
                                delete_time=None
                            )
                            if customerT.count() > 0:
                                d_flag = 1
                                samp = {}
                                samp['msg'] = "唛头已经存在"
                                samp['key_num'] = done['brand']
                                l_msg.append(samp)
                            else:
                                bObj = Marks()
                                bObj.create_time = dt
                                bObj.namecard_id = done['namecard_id']
                                bObj.brand = done['brand']
                                bObj.brand_url = done['brand_url']
                                bObj.active = done['active']
                                bObj.save()
                    except:
                        msg = "参数校验不通过！"
                        error_code = 10030
                        request = request.method + '  ' + request.get_full_path()
                        post_result = {
                            "error_code": error_code,
                            "message": msg,
                            "request": request,
                        }
                        return Response(post_result)
                if d_flag ==0:
                    msg = "创建联系方式"
                    error_code = 0
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
            msg = "客户档案不存在"
            error_code = 404
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
    # 唛头更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = marksOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Marks.objects.get(id=nid)
            bObj.brand = data['brand']
            if data['brand_url']:
                bObj.brand_url = data['brand_url']
            bObj.active = data['active']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新唛头成功!",
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
    #删除 唛头
    @csrf_exempt
    def delete(self, request, nid):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = Marks.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "唛头删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "唛头不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


#*******************************员工管理****************************************************
############################资料设置###############################################
class departmentView(APIView):
    # 部门岗位
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = departmentSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = Department.objects.filter(delete_time=None).order_by('weight')
                department_name = valObj.data['department_name'] if valObj.data['department_name'] is not None else ''
                if department_name:
                    rObj = rObj.filter(department_name__contains=department_name)
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["department_name"] = one.department_name
                    temp['id'] = one.id
                    post = Post.objects.filter(delete_time=None,department_id=one.id)
                    samp = []
                    for o in post:
                        sampd = {}
                        if o.active == 1:
                            sampd['active'] = True
                        else:
                            sampd['active'] = False
                        sampd['department_id'] = o.department_id
                        sampd['id'] = o.id
                        sampd['post_name'] = o.post_name
                        sampd['weight'] = o.weight
                        samp.append(sampd)
                    temp['post'] = samp
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的部门岗位"
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

    # 添加部门岗位
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = departmentOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = departmentOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = Department.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.department_name = done['department_name']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        depart = Department.objects.filter(
                            department_name=done['department_name'],
                            delete_time=None
                        )
                        if depart.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "部门已经存在"
                            samp['key_num'] = done['department_name']
                            l_msg.append(samp)
                        else:
                            bObj = Department()
                            bObj.create_time = dt
                            num = Department.objects.all().count() + 1
                            bObj.department_name = done['department_name']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag==0:
                msg = "创建部门"
                error_code = 0
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
                bObj = Department.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "部门岗位删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "部门岗位不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class departmentOneView(APIView):
    #客户类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = departmentOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Department.objects.get(id=nid)
            bObj.active = data['active']
            bObj.department_name = data['department_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新客户类型成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Department.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "部门删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "客户类型不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class departmentSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = Department.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = Department.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "客户类型排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################资料设置###############################################
class departmentPostView(APIView):

    # 添加部门岗位
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = postOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = postOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = Post.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.post_name = done['post_name']
                        bObj.department_id = done['department_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        post = Post.objects.filter(
                            post_name=done['post_name'],
                            department_id=done['department_id'],
                            delete_time=None
                        )
                        if post.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "岗位已经存在"
                            samp['key_num'] = done['department_name']
                            l_msg.append(samp)
                        else:
                            bObj = Post()
                            bObj.create_time = dt
                            num = Post.objects.all().count() + 1
                            bObj.post_name = done['post_name']
                            bObj.department_id = done['department_id']
                            bObj.active = done['active']
                            if not mid:
                                bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag ==0:
                msg = "创建部门岗位"
                error_code = 0
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
                bObj = Post.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "岗位删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "岗位不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class departmentPostOneView(APIView):
    # 部门岗位
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        fdeoart = Department.objects.filter(id=nid, delete_time=None)
        if fdeoart.count()>0:
            result = []
            try:
                rObj = Post.objects.filter(department_id=nid,delete_time=None).order_by('weight')
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["post_name"] = one.post_name
                    temp['post_id'] = one.id
                    temp["department_id"] = one.department_id
                    temp['department_name'] = fdeoart[0].department_name
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的部门岗位"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        else:
            msg = "未找到对应的部门岗位"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #客户类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = postUOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Post.objects.get(id=nid)
            bObj.active = data['active']
            bObj.post_name = data['post_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新岗位成功!",
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
    #删除岗位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Post.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "部门岗位删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "岗位不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class departmentPostSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = Post.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = Post.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "岗位排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################工号设置###############################################
class job_numberView(APIView):
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = jobnumberSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = JobNumber.objects.filter(id=1)
                sort_type = valObj.data['sort_type'] if valObj.data['sort_type'] is not None else 0
                for one in rObj:
                    temp = {}
                    temp["end_number"] = one.end_number
                    temp['id'] = one.id
                    temp['sort_type'] = one.sort_type
                    temp['start_number'] = one.start_number
                    result.append(temp)
                return Response(result)
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

class job_numberOneView(APIView):
    #工号设置更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = jobnumOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = JobNumber.objects.get(id=nid)
            bObj.end_number = data['end_number']
            bObj.sort_type = data['sort_type']
            bObj.start_number = data['start_number']
            bObj.update_timactivee = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新工号设置成功!",
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



############################入离职资料###############################################
class templateOneView(APIView):
    # 入职资料
    @csrf_exempt
    def get(self, request, nid):
        result = []
        try:
            rObj = DataTemplate.objects.filter(type_id=nid, delete_time=None).order_by('weight')
            for one in rObj:
                temp = {}
                if one.active == 1:
                    temp['active'] = True
                else:
                    temp['active'] = False
                if one.required == 1:
                    temp['required'] = True
                else:
                    temp['required'] = False
                temp["name"] = one.name
                temp['id'] = one.id
                temp['template_url'] = one.template_url
                temp['weight'] = one.weight
                result.append(temp)
            return Response(result)
        except:
            msg = "未找到对应的入职资料"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


    # 添加入职资料
    @csrf_exempt
    def post(self, request, nid):
        # data = request.query_params
        # valObj = templateOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = templateOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = DataTemplate.objects.get(id=mid)
                        bObj.update_time = dt
                        num = DataTemplate.objects.all().count() + 1

                        bObj.name = done['name']
                        bObj.template_url = done['template_url']
                        bObj.required = done['required']
                        bObj.active = done['active']
                        if not mid:
                            bObj.weight = num
                        bObj.save()
                    else:
                        datat = DataTemplate.objects.filter(
                            name=done['name'],
                            type_id=done['type_id'],
                            delete_time=None
                        )
                        if datat.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "资料模板已经存在"
                            samp['key_num'] = done['name']
                            l_msg.append(samp)
                        else:
                            bObj = DataTemplate()
                            bObj.create_time = dt
                            num = DataTemplate.objects.all().count() + 1

                            bObj.name = done['name']
                            bObj.template_url = done['template_url']
                            bObj.required = done['required']
                            bObj.active = done['active']
                            bObj.type_id = done['type_id']
                            if not mid:
                                bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag==0:
                msg = "创建资料模版"
                error_code = 0
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
            msg = l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #客户类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = templateOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = DataTemplate.objects.get(id=nid)
            bObj.active = data['active']
            bObj.name = data['name']
            bObj.required = data['required']
            bObj.template_url = data['template_url']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新客户类型成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = DataTemplate.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "资料模版删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "客户类型不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class templateSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = DataTemplate.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = DataTemplate.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "资料模版排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################入离职档案设置###############################################
class archiveView(APIView):
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = archivesSerializer(data=request.query_params)
        if valObj.is_valid():
            start, page_size, flag = zddpaginate(int(data['page']), int(data['page_size']))
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
                rObj = Archives.objects.filter(delete_time=None)
                status = valObj.data['status'] if valObj.data['status'] is not None else 2
                department_id = valObj.data['department_id'] if valObj.data['department_id'] is not None else 0
                post_id = valObj.data['post_id'] if valObj.data['post_id'] is not None else 0
                name = valObj.data['name'] if valObj.data['name'] is not None else ""
                if status != 2:
                    rObj = rObj.filter(status = status)
                if department_id:
                    rObj = rObj.filter(department_id = department_id)
                if post_id:
                    rObj = rObj.filter(post_id = post_id)
                if name:
                    rObj = rObj.filter(name__contains = name)
                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start+page_size].values()
                    temp = {}
                    temp["data"] = rObj
                    temp['page_size'] = page_size
                    temp['total'] = total
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = rObj
                    temp['page_size'] = page_size
                    temp['total'] = total
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

    # 添加员工档案
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = archivesOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = archivesOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = Archives.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.job_number = get_member_N()
                        bObj.name = done['name']
                        bObj.gender = done['gender']
                        bObj.birthday = done['birthday']
                        bObj.department_id = done['department_id']
                        bObj.post_id = done['post_id']
                        bObj.phone = done['phone']
                        bObj.emergency_contact = done['emergency_contact']
                        bObj.emergency_phone = done['emergency_phone']
                        bObj.due_to_time = done['due_to_time']
                        bObj.enter_time = done['enter_time']
                        bObj.leave_time = done['leave_time']
                        bObj.status = 1
                        bObj.save()
                    else:
                        archives = Archives.objects.filter(
                            name=done['name'],
                            delete_time=None
                        )
                        if archives.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "员工档案已经存在"
                            samp['key_num'] = done['name']
                            l_msg.append(samp)
                        else:
                            bObj = Archives()
                            bObj.create_time = dt
                            bObj.job_number = get_member_N()
                            bObj.name = done['name']
                            bObj.gender = done['gender']
                            bObj.birthday = done['birthday']
                            bObj.department_id = done['department_id']
                            bObj.post_id = done['post_id']
                            bObj.phone = done['phone']
                            bObj.emergency_contact = done['emergency_contact']
                            bObj.emergency_phone = done['emergency_phone']
                            bObj.due_to_time = done['due_to_time']
                            bObj.enter_time = done['enter_time']
                            bObj.leave_time = done['leave_time']
                            bObj.status = 1
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag ==0:
                msg = "创建员工档案"
                error_code = 0
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
                bObj = Archives.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "员工档案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "员工档案不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class archiveOneView(APIView):
    #员工档案更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = archivesOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Archives.objects.get(id=nid)
            bObj.name = data['name']
            bObj.gender = data['gender']
            bObj.birthday = data['birthday']
            bObj.department_id = data['department_id']
            bObj.post_id = data['post_id']
            bObj.phone = data['phone']
            bObj.status = data['status']
            bObj.emergency_contact = data['emergency_contact']
            bObj.emergency_phone = data['emergency_phone']
            bObj.due_to_time = data['due_to_time']
            bObj.update_time = dt
            bObj.enter_time = data['enter_time']
            bObj.leave_time = data['leave_time']
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新工号设置成功!",
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

        # 删除用料单位

    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Archives.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "员工档案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "员工档案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################入离职资料上传设置###############################################
class archiveInFile(APIView):
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = archivesFileOneSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = DataTemplate.objects.filter(delete_time=None,type_id=data['type_id'])
                for one in rObj:
                    samp = {}
                    dtaObj = DataTemplateArchives.objects.filter(type_id=data['type_id'],
                                                                 archives_id=data['archives_id'],template_id=one.id)
                    if dtaObj.count()>0:
                        samp['name'] = dtaObj[0].name
                        samp['type_id'] = dtaObj[0].type_id
                        samp['template_url'] = dtaObj[0].template_url
                        samp['template_id'] = dtaObj[0].template_id
                        samp['id'] = dtaObj[0].id
                        samp['required'] = one.required
                        samp['status'] = 1
                        result.append(samp)
                    else:
                        samp['name'] = one.name
                        samp['type_id'] = one.type_id
                        samp['template_url'] = ""
                        samp['template_id'] = one.id
                        samp['required'] = one.required
                        samp['id'] = 0
                        samp['status'] = 0
                        result.append(samp)

                temp = {}
                temp["data"] = result
                temp['error_code'] = 0
                temp['message'] = "获取成功"
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

    # 添加员工档案
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = archivesFileSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = DataTemplateArchives.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.template_url = done['template_url']
                        bObj.name = done['name']
                        bObj.type_id = done['type_id']
                        bObj.archives_id = done['archives_id']
                        bObj.template_id = done['template_id']
                        bObj.save()
                    else:
                        archives = DataTemplateArchives.objects.filter(
                            name=done['name'],
                            type_id = done['type_id'],
                            delete_time=None
                        )
                        if archives.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "员工档案资料已经存在"
                            samp['key_num'] = done['name']
                            l_msg.append(samp)
                        else:
                            bObj = DataTemplateArchives()
                            bObj.create_time = dt
                            bObj.template_url = done['template_url']
                            bObj.name = done['name']
                            bObj.type_id = done['type_id']
                            bObj.archives_id = done['archives_id']
                            bObj.template_id = done['template_id']
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag ==0:
                msg = "录入员工档案资料"
                error_code = 0
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
                bObj = Archives.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "员工档案删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "员工档案不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class archiveInFileOneView(APIView):
    #员工档案更新-active
    @csrf_exempt
    def post(self, request, nid):
        data = request.query_params
        valObj = archivesOneEditSerializer(data=request.query_params)
        if valObj.is_valid():
            type_id = valObj.data['type_id'] if valObj.data['type_id'] is not None else 0
            birthday_mouth = valObj.data['birthday_mouth'] if valObj.data['birthday_mouth'] is not None else 0
            birthday_day = valObj.data['birthday_day'] if valObj.data['birthday_day'] is not None else 0
            leave_time = valObj.data['leave_time'] if valObj.data['leave_time'] is not None else ""
            dt = datetime.now()
            bObj = Archives.objects.get(id=nid)
            if type_id==1:
                bObj.birthday_mouth = birthday_mouth
                bObj.birthday_day = birthday_day
                bObj.update_time = dt
                bObj.save()
            else:
                bObj.leave_time = leave_time
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新入离职资料成功!",
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

#*******************************注意事项****************************************************
############################类别设置###############################################
class categoryView(APIView):
    # 类别设置
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = categorySerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = Cloth.objects.filter(delete_time=None).order_by('weight')
                cloth_class_id = valObj.data['cloth_class_id'] if valObj.data['cloth_class_id'] is not None else 0
                cloth_id = valObj.data['cloth_id'] if valObj.data['cloth_id'] is not None else 0
                if cloth_class_id:
                    rObj = rObj.filter(class_id=cloth_class_id)
                if cloth_id:
                    rObj = rObj.filter(id=cloth_id)
                for one in rObj:
                    ccobj = ClothClass.objects.filter(id=one.class_id, delete_time=None)
                    if ccobj.count() > 0:
                        temp = {}
                        temp["cloth_class_name"] = ccobj[0].cloth_class_name
                        temp["cloth_class_id"] = one.class_id
                        temp["cloth_name"] = one.cloth
                        temp['cloth_id'] = one.id
                        subcat = ClothCategory.objects.filter(cloth_id=one.id,delete_time=None)
                        samp = []
                        for o in subcat:
                            sampd = {}
                            if o.active == 1:
                                sampd['active'] = True
                            else:
                                sampd['active'] = False
                            sampd['category_name'] = o.category_name
                            sampd['category_id'] = o.id
                            sampd['cloth_id'] = o.cloth_id
                            sampd['cloth_name'] = one.cloth
                            sampd['delete_time'] = one.delete_time
                            sampd['weight'] = o.weight
                            samp.append(sampd)
                        temp['category'] = samp
                        result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的类别设置"
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

    # 添加
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = categoryOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = categoryOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = ClothCategory.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.category_name = done['category_name']
                        bObj.cloth_id = done['cloth_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        ccat = ClothCategory.objects.filter(
                            category_name=done['category_name'],
                            cloth_id=done['cloth_id'],
                            delete_time=None
                        )
                        if ccat.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "注意事项类别已经存在"
                            samp['key_num'] = done['category_name']
                            l_msg.append(samp)
                        else:
                            bObj = ClothCategory()
                            bObj.create_time = dt
                            num = ClothCategory.objects.all().count() + 1
                            bObj.category_name = done['category_name']
                            bObj.cloth_id = done['cloth_id']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag ==0:
                msg = "创建注意事项类别"
                error_code = 0
            else:
                msg =l_msg
                error_code = 10030
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
                bObj = ClothCategory.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "类别设置删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "类别设置不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)



class categoryOneView(APIView):
    #-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = categoryUOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ClothCategory.objects.get(id=nid)
            bObj.active = data['active']
            bObj.category_name = data['category_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新注意事项类别成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ClothCategory.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "注意事项类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "注意事项类别不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class categorySortView(APIView):
    #注意事项类别排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ClothCategory.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ClothCategory.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "注意事项类别排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################类别设置###############################################
class notesView(APIView):
    # 注意事项
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = categoryNoteGetSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = ClothCategory.objects.filter(delete_time=None).order_by('weight')
                cloth_class_id = valObj.data['cloth_class_id'] if valObj.data['cloth_class_id'] is not None else 0
                cloth_id = valObj.data['cloth_id'] if valObj.data['cloth_id'] is not None else 0
                cloth_category_id = valObj.data['cloth_category_id'] if valObj.data['cloth_category_id'] is not None else 0
                if cloth_class_id:
                    clothObj = Cloth.objects.filter(class_id = cloth_class_id)
                    if clothObj.count()>0:
                        ids = [one.id for one in clothObj]
                        rObj = rObj.filter(cloth_id__in=ids)
                if cloth_id:
                    rObj = rObj.filter(cloth_id=cloth_id)
                if cloth_category_id:
                    rObj = rObj.filter(id=cloth_category_id)
                for one in rObj:
                    cobj = Cloth.objects.filter(id=one.cloth_id, delete_time=None)
                    if cobj.count()>0:
                        ccobj = ClothClass.objects.filter(id=cobj[0].class_id, delete_time=None)
                        if ccobj.count() > 0:
                            temp = {}
                            temp["cloth_class_name"] = ccobj[0].cloth_class_name
                            temp["cloth_class_id"] = ccobj[0].id
                            temp["category_name"] = one.category_name
                            temp['category_id'] = one.id
                            temp["cloth_name"] = cobj[0].cloth
                            temp['cloth_id'] = cobj[0].id
                            subnotes = ClothNotes.objects.filter(category_id=one.id,delete_time=None).order_by('weight')
                            samp = []
                            for o in subnotes:
                                sampd = {}
                                if o.active == 1:
                                    sampd['active'] = True
                                else:
                                    sampd['active'] = False
                                sampd['category_name'] = one.category_name
                                sampd['category_id'] = o.category_id
                                sampd['notes_id'] = o.id
                                sampd['notes_name'] = o.notes_name
                                sampd['delete_time'] = o.delete_time
                                sampd['weight'] = o.weight
                                samp.append(sampd)
                            temp['notes'] = samp
                            result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的注意事项"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)

    # 添加
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = notesOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = notesOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = ClothNotes.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.notes_name = done['notes_name']
                        bObj.category_id = done['category_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        ccat = ClothNotes.objects.filter(
                            notes_name=done['notes_name'],
                            category_id=done['category_id'],
                            delete_time=None
                        )
                        if ccat.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "注意事项内容已经存在"
                            samp['key_num'] = done['notes_name']
                            l_msg.append(samp)
                        else:
                            bObj = ClothNotes()
                            bObj.create_time = dt
                            num = ClothNotes.objects.all().count() + 1
                            bObj.notes_name = done['notes_name']
                            bObj.category_id = done['category_id']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建注意事项"
                error_code = 0
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
            msg =l_msg
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
                bObj = ClothNotes.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
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
            msg = "注意事项不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class notesOneView(APIView):
    #-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = notesUOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ClothNotes.objects.get(id=nid)
            bObj.active = data['active']
            bObj.notes_name = data['notes_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新注意事项成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ClothNotes.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
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

class notesSortView(APIView):
    #注意事项类别排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ClothNotes.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ClothNotes.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "注意事项排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################类别设置###############################################
class category_setView(APIView):
    # 部门岗位
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = othercategorySerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = OtherSubCategory.objects.filter(delete_time=None).order_by('weight')
                category_id = valObj.data['category_id'] if valObj.data['category_id'] is not None else 0
                sub_category_id = valObj.data['sub_category_id'] if valObj.data['sub_category_id'] is not None else 0
                if category_id:
                    rObj = rObj.filter(category_id=category_id)
                if sub_category_id:
                    rObj = rObj.filter(id=sub_category_id)
                for one in rObj:
                    pobj = OtherCategory.objects.filter(id=one.category_id, delete_time=None)
                    if pobj.count() > 0:
                        temp = {}
                        temp["category_id"] = pobj[0].id
                        temp["cat_name"] = pobj[0].category_name
                        temp["sub_name"] = one.sub_name
                        temp['sub_category_id'] = one.id
                        subcat = OtherCategorySetting.objects.filter(sub_category_id=one.id,delete_time=None)
                        samp = []
                        for o in subcat:
                            sampd = {}
                            if o.active == 1:
                                sampd['active'] = True
                            else:
                                sampd['active'] = False
                            sampd['category_set_name'] = o.category_set_name
                            sampd['category_setting_id'] = o.id
                            sampd['sub_category_id'] = o.sub_category_id
                            sampd['sub_name'] = one.sub_name
                            sampd['delete_time'] = o.delete_time
                            sampd['weight'] = o.weight
                            samp.append(sampd)
                        temp['sub_category'] = samp
                        result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的类别设置"
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

    # 添加
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = ocategoryOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = ocategoryOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = OtherCategorySetting.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.category_set_name = done['category_set_name']
                        bObj.sub_category_id = done['sub_category_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        ccat = OtherCategorySetting.objects.filter(
                            category_set_name=done['category_set_name'],
                            sub_category_id=done['sub_category_id'],
                            delete_time=None
                        )
                        if ccat.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "其他注意事项已经存在"
                            samp['key_num'] = done['category_name']
                            l_msg.append(samp)
                        else:
                            bObj = OtherCategorySetting()
                            bObj.create_time = dt
                            num = OtherCategorySetting.objects.all().count() + 1
                            bObj.category_set_name = done['category_set_name']
                            bObj.sub_category_id = done['sub_category_id']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag==0:
                msg = "创建其他注意事项类别"
                error_code = 0
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
                bObj = OtherCategorySetting.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "其他注意事项类别不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class category_setOneView(APIView):
    #-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = ocategoryUOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = OtherCategorySetting.objects.get(id=nid)
            bObj.active = data['active']
            bObj.category_name = data['category_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新其他注意事项类别成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = OtherCategorySetting.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "其他注意事项类别不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class category_setSortView(APIView):
    #注意事项类别排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = OtherCategorySetting.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = OtherCategorySetting.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "注意事项类别排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################其他类别设置###############################################
class other_categoryView(APIView):
    # 部门岗位
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = othercategerSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = OtherCategory.objects.filter(delete_time=None).order_by('weight')
                category_name = valObj.data['category_name'] if valObj.data['category_name'] is not None else ""
                if category_name:
                    rObj = rObj.filter(category_name__contains=category_name)
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["category_name"] = one.category_name
                    temp["weight"] = one.weight
                    temp['id'] = one.id
                    subcat = OtherSubCategory.objects.filter(category_id=one.id, delete_time=None)
                    samp = []
                    for o in subcat:
                        sampd = {}
                        if o.active == 1:
                            sampd['active'] = True
                        else:
                            sampd['active'] = False
                        sampd['sub_name'] = o.sub_name
                        sampd['id'] = o.id
                        sampd['category_id'] = o.category_id
                        sampd['delete_time'] = o.delete_time
                        sampd['weight'] = o.weight
                        samp.append(sampd)
                    temp['sub_category'] = samp
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到类别分类"
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

    # 添加
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = othercategerOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = othercategerOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = OtherCategory.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.category_name = done['category_name']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        ccat = OtherCategory.objects.filter(
                            category_name=done['category_name'],
                            delete_time=None
                        )
                        if ccat.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "类别已经存在"
                            samp['key_num'] = done['category_name']
                            l_msg.append(samp)
                        else:
                            bObj = OtherCategory()
                            bObj.create_time = dt
                            num = OtherCategory.objects.all().count() + 1
                            bObj.category_name = done['category_name']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()

                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag==0:
                msg = "创建其他注意事项类别"
                error_code = 0
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
                bObj = OtherCategory.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "其他注意事项类别不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class other_categoryOneView(APIView):
    #-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = othercategerOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = OtherCategory.objects.get(id=nid)
            bObj.active = data['active']
            bObj.category_name = data['category_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新其他注意事项类别成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = OtherCategory.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "其他注意事项类别不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class other_categorySortView(APIView):
    #注意事项类别排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = OtherCategory.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = OtherCategory.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "注意事项类别排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################其他类别名称###############################################
class sub_categoryView(APIView):

    # 添加
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = ocategorysubOneSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = ocategorysubOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = OtherSubCategory.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.sub_name = done['sub_name']
                        bObj.category_id = done['category_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        ccat = OtherSubCategory.objects.filter(
                            sub_name=done['sub_name'],
                            category_id=done['category_id'],
                            delete_time=None
                        )
                        if ccat.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "类别已经存在"
                            samp['key_num'] = done['sub_name']
                            l_msg.append(samp)
                        else:
                            bObj = OtherSubCategory()
                            bObj.create_time = dt
                            num = OtherSubCategory.objects.all().count() + 1
                            bObj.sub_name = done['sub_name']
                            bObj.category_id = done['category_id']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()

                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建其他注意事项类别"
                error_code = 0
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
                bObj = OtherSubCategory.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "其他注意事项类别不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class sub_categoryOneView(APIView):
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        result = []
        try:
            rObj = OtherSubCategory.objects.filter(category_id=nid, delete_time=None).order_by('weight')
            cObj = OtherCategory.objects.filter(id=nid)
            if cObj.count() >0:
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["category_name"] = cObj[0].category_name
                    temp["category_id"] = one.category_id
                    temp["weight"] = one.weight
                    temp['sub_category_id'] = one.id
                    temp['sub_name'] = one.sub_name
                    result.append(temp)
                return Response(result)
        except:
            msg = "未找到类别分类"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = ocategorysubUOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = OtherSubCategory.objects.get(id=nid)
            bObj.active = data['active']
            bObj.sub_name = data['sub_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新其他注意事项类别成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = OtherSubCategory.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项类别删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "其他注意事项类别不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################类别设置###############################################
class other_notesView(APIView):
    # 注意事项
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = othercategoryNoteGetSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = OtherSubCategory.objects.filter(delete_time=None).order_by('weight')
                category_id = valObj.data['category_id'] if valObj.data['category_id'] is not None else 0
                sub_category_id = valObj.data['sub_category_id'] if valObj.data['sub_category_id'] is not None else 0
                otehr_cat_set_id = valObj.data['otehr_cat_set_id'] if valObj.data['otehr_cat_set_id'] is not None else 0
                if category_id:
                    rObj = rObj.filter(category_id=category_id)
                if sub_category_id:
                    rObj = rObj.filter(id=sub_category_id)
                if otehr_cat_set_id:
                    setObj = OtherCategorySetting.objects.get(id=otehr_cat_set_id)
                    rObj = rObj.filter(id=setObj.sub_category_id)
                for one in rObj:
                    pobj = OtherCategory.objects.filter(id=one.category_id, delete_time=None)
                    if pobj.count() > 0:
                        temp = {}
                        temp["category_id"] = pobj[0].id
                        temp["category_name"] = pobj[0].category_name
                        temp["sub_name"] = one.sub_name
                        temp['sub_category_id'] = one.id
                        subcat = OtherCategorySetting.objects.filter(sub_category_id=one.id, delete_time=None)
                        ids = [one.id for one in subcat]
                        ssubcat = OtherNotes.objects.filter(category_setting_id__in=ids).order_by("category_setting_id")
                        ssamp=[]
                        for subone in ssubcat:
                            subcatone = OtherCategorySetting.objects.get(id=subone.category_setting_id)
                            sampd = {}
                            if subone.active == 1:
                                sampd['active'] = True
                            else:
                                sampd['active'] = False
                            sampd['notes_name'] = subone.notes_name
                            sampd['weight'] = subone.weight
                            sampd['notes_id'] = subone.id
                            sampd['category_set_name'] = subcatone.category_set_name
                            sampd['cat_set_id'] = subcatone.id
                            ssamp.append(sampd)

                        temp['notes'] = ssamp
                        result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的类别设置"
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


    # 添加
    @csrf_exempt
    def post(self, request):
        # data = request.query_params
        # valObj = otherNotesSerializer(data=request.query_params)
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = otherNotesSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = OtherNotes.objects.get(id=mid)
                        bObj.update_time = dt
                        bObj.notes_name = done['notes_name']
                        bObj.category_setting_id = done['cat_set_id']
                        bObj.active = done['active']
                        bObj.save()
                    else:
                        ccat = OtherNotes.objects.filter(
                            notes_name=done['notes_name'],
                            category_setting_id=done['cat_set_id'],
                            delete_time=None
                        )
                        if ccat.count() > 0:
                            d_flag = 1
                            samp = {}
                            samp['msg'] = "其他注意事项已经存在"
                            samp['key_num'] = done['notes_name']
                            l_msg.append(samp)
                        else:
                            bObj = OtherNotes()
                            bObj.create_time = dt
                            num = OtherNotes.objects.all().count() + 1
                            bObj.notes_name = done['notes_name']
                            bObj.category_setting_id = done['cat_set_id']
                            bObj.active = done['active']
                            bObj.weight = num
                            bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建注意事项"
                error_code = 0
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
                bObj = OtherNotes.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "注意事项内容删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "注意事项内容不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)


class other_notesOneView(APIView):
    #-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = otherNotesUSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = OtherNotes.objects.get(id=nid)
            bObj.active = data['active']
            bObj.notes_name = data['notes_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "其他注意事项内容更新成功!",
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
    #删除
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = OtherNotes.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
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

class other_notesSortView(APIView):
    #注意事项类别排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = OtherNotes.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = OtherNotes.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "注意事项排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################在建企划###############################################
# 获取企划详情
def getPlanSub(plan_id):
    sub = {}
    pricePlan = PlanPrice.objects.filter(plan_id=plan_id,delete_time=None)
    mPlanMaterial = PlanMaterial.objects.filter(plan_id=plan_id,delete_time=None)
    mPriceSub = PlanPriceSub.objects.filter(plan_id=plan_id,delete_time=None)
    if pricePlan.count()>0:
        #用料不同显示
        mPlanMaterialOld = PlanMaterialCopy.objects.filter(plan_id=plan_id)
        mPriceSubOld = PlanPriceSubCopy.objects.filter(plan_id=plan_id)
        sub['mPlanMaterial'] = vsTable(mPlanMaterial,mPlanMaterialOld)
        sub['mPriceSub'] = vsTable(mPriceSub, mPriceSubOld)
    else:
        sub['mPlanMaterial'] = mPlanMaterial.values()
        sub['mPriceSub'] = mPriceSub.values()
    sub['priceplan'] = pricePlan.values()
    return sub

# 获取企划历史详情
def getPlanHistory(plan_id,edition):
    sub = {}
    mPlanMaterialOld = PlanMaterialCopy.objects.filter(plan_id=plan_id,edition=edition)
    mPriceSubOld = PlanPriceSubCopy.objects.filter(plan_id=plan_id,edition=edition)
    planPriceOld = PlanPriceCopy.objects.filter(plan_id=plan_id,edition=edition)
    sub['mPlanMaterial'] = mPlanMaterialOld.values()
    sub['mPriceSub'] =mPriceSubOld.values()
    sub['priceplan'] = planPriceOld.values()
    return sub

class planView(APIView):
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = planSerializer(data=request.query_params)
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
                rObj = Plan.objects.filter(delete_time=None)
                customer_name_id = valObj.data['customer_name_id'] if valObj.data['customer_name_id'] is not None else 0
                brand_id = valObj.data['brand_id'] if valObj.data['brand_id'] is not None else 0
                start_time = valObj.data['start_time'] if valObj.data['start_time'] is not None else 0
                end_time = valObj.data['end_time'] if valObj.data['end_time'] is not None else 0
                price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                status = valObj.data['status'] if valObj.data['status'] is not None else 0
                if status==4:
                    rObj = Plan.objects.filter(status=status)
                elif status==0:
                    rObj = rObj.filter(status__in=[0,1,2])
                else:
                    rObj = rObj.filter(status=status)
                if customer_name_id != 0:
                    rObj = rObj.filter(customer_name_id = customer_name_id)
                if brand_id:
                    rObj = rObj.filter(brand_id = brand_id)
                if price_code:
                    rObj = rObj.filter(price_code__contains = price_code)
                if start_time:
                    rObj = rObj.filter(plan_datetime__gte = start_time)
                if end_time:
                    rObj = rObj.filter(plan_datetime__lte = end_time)

                total = rObj.count()
                if rObj.count() > start:
                    rObj = rObj.all()[start:start+page_size]
                    result = []
                    for one in rObj:
                        samp = {}
                        samp['id'] = one.id
                        samp['create_time'] = one.create_time
                        samp['delete_time'] = one.delete_time
                        samp['plan_datetime'] = one.plan_datetime
                        samp['customer_name_id'] = one.customer_name_id
                        cusObj = CustomerFiles.objects.get(id=one.customer_name_id)
                        samp['company_name_simple'] = cusObj.customer_simple_name
                        samp['brand_id'] = one.brand_id
                        bobj = Marks.objects.get(id=one.brand_id)
                        samp['brand'] = bobj.brand
                        samp['plan_org_post'] = one.plan_org_post
                        samp['plan_org_department'] = one.plan_org_department
                        samp['plan_org_id'] = one.plan_org_id
                        pObj1 = Archives.objects.get(id=one.plan_org_id)
                        samp['plan_org_er'] = pObj1.name
                        samp['plan_department'] = one.plan_department
                        samp['plan_post'] = one.plan_post
                        samp['plan_id'] = one.plan_id
                        pObj2 = Archives.objects.get(id=one.plan_id)
                        samp['plan_er'] = pObj2.name
                        samp['material_plan_department'] = one.material_plan_department
                        samp['material_plan_post'] = one.material_plan_post
                        samp['material_plan_id'] = one.material_plan_id
                        pObj3 = Archives.objects.get(id=one.material_plan_id)
                        samp['material_plan_er'] = pObj3.name
                        samp['price_id'] = one.price_id
                        samp['price_post'] = one.price_post
                        samp['price_department'] = one.price_department
                        pObj4 = Archives.objects.get(id=one.price_id)
                        samp['price_er'] = pObj4.name
                        samp['goods_name'] = one.goods_name
                        samp['price_code'] = one.price_code
                        samp['status'] = one.status
                        if one.status == 0:
                            samp['contenter'] = pObj1.name
                            samp['contenting'] = "企划组织"
                        if one.status == 1:
                            samp['contenter'] = pObj3.name
                            samp['contenting'] = "企划用料"
                        if one.status == 2:
                            samp['contenter'] = pObj4.name
                            samp['contenting'] = "企划报价"
                        if one.status == 3:
                            samp['contenter'] = pObj2.name
                            samp['contenting'] = "企划完成"
                        result.append(samp)
                    temp = {}
                    temp["data"] = result
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                else:
                    temp = {}
                    temp["data"] = rObj
                    temp['page_size'] = page_size
                    temp['total'] = total
                    temp['error_code'] = 0
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

    # 添加员工档案
    @csrf_exempt
    def post(self, request):
        data = request.query_params
        valObj = planOneSerializer(data=request.query_params)
        dt = datetime.now()
        if valObj.is_valid():
            try:
                plan = Plan.objects.filter(
                    goods_name=data['goods_name'],
                    price_code=data['price_code'],
                    brand_id=data['brand_id'],
                    delete_time=None
                )
                if plan.count() > 0:
                    msg = "企划方案已存在"
                    error_code = 400
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
                else:
                    bObj = Plan()
                    bObj.status = 0
                    bObj.brand_id = data['brand_id']
                    bObj.customer_name_id = data['customer_name_id']
                    bObj.plan_id = data['plan_id']
                    bObj.plan_department = data['plan_department']
                    bObj.plan_post = data['plan_post']
                    bObj.plan_org_id = data['plan_org_id']
                    bObj.plan_org_department = data['plan_org_department']
                    bObj.plan_org_post = data['plan_org_post']
                    bObj.price_post = data['price_post']
                    bObj.price_department = data['price_department']
                    bObj.price_id = data['price_id']
                    bObj.material_plan_id = data['material_plan_id']
                    bObj.material_plan_department = data['material_plan_department']
                    bObj.material_plan_post = data['material_plan_post']
                    bObj.goods_name = data['goods_name']
                    bObj.price_code = data['price_code']
                    bObj.plan_datetime = data['plan_datetime']
                    bObj.edition = 0
                    bObj.create_time = dt
                    bObj.save()
                    msg = "创建在建企划"
                    error_code = 0
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            except:
                msg = "参数校验不通过！"
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

    #删除企划以及相关的企划内容
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids= data['ids']
            for one in ids:
                bObj = Plan.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.status = 5
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划关闭成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "在建企划不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class planOneView(APIView):
    #企划更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = planOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = Plan.objects.get(id=nid)
            bObj.brand_id = data['brand_id']
            bObj.customer_name_id = data['customer_name_id']
            bObj.plan_id = data['plan_id']
            bObj.plan_org_id = data['plan_org_id']
            bObj.price_id = data['price_id']
            bObj.material_plan_id = data['material_plan_id']
            bObj.goods_name = data['goods_name']
            bObj.price_code = data['price_code']
            bObj.plan_datetime = data['plan_datetime']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新在建企划成功!",
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

        # 删除用料单位

    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = Plan.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.status = 4
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划关闭成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "在建企划不存在!",
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
        data = request.query_params
        valObj = planSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = Plan.objects.filter(delete_time=None, id=nid)
                if rObj.count()>0:
                    one = rObj[0]
                    samp = {}
                    samp['plan_datetime'] = one.plan_datetime
                    samp['customer_name_id'] = one.customer_name_id
                    cusObj = CustomerFiles.objects.get(id=one.customer_name_id)
                    samp['company_name_simple'] = cusObj.customer_simple_name
                    samp['customer_type_id'] = cusObj.type_id
                    samp['brand_id'] = one.brand_id
                    bobj = Marks.objects.get(id=one.brand_id)
                    samp['brand'] = bobj.brand
                    samp['plan_org_id'] = one.plan_org_id
                    pObj1 = Archives.objects.get(id=one.plan_org_id)
                    pDObj1 = Department.objects.get(id=pObj1.department_id)
                    pPObj1 = Post.objects.get(id=pObj1.post_id)
                    samp['plan_org_department'] = pDObj1.department_name
                    samp['plan_org_post'] = pPObj1.post_name
                    samp['plan_org_er'] = pObj1.name
                    samp['plan_id'] = one.plan_id
                    pObj2 = Archives.objects.get(id=one.plan_id)
                    pDObj2 = Department.objects.get(id=pObj2.department_id)
                    pPObj2 = Post.objects.get(id=pObj2.post_id)
                    samp['plan_department'] = pDObj2.department_name
                    samp['plan_post'] = pPObj2.post_name
                    samp['plan_er'] = pObj2.name
                    samp['material_plan_id'] = one.material_plan_id
                    pObj3 = Archives.objects.get(id=one.material_plan_id)
                    pDObj3 = Department.objects.get(id=pObj3.department_id)
                    pPObj3 = Post.objects.get(id=pObj3.post_id)
                    samp['material_plan_department'] = pDObj3.department_name
                    samp['material_plan_post'] = pPObj3.post_name
                    samp['material_plan_er'] = pObj3.name
                    samp['price_id'] = one.price_id
                    pObj4 = Archives.objects.get(id=one.price_id)
                    pDObj4 = Department.objects.get(id=pObj4.department_id)
                    pPObj4 = Post.objects.get(id=pObj4.post_id)
                    samp['price_department'] = pDObj4.department_name
                    samp['price_post'] = pPObj4.post_name
                    samp['price_er'] = pObj4.name
                    samp['goods_name'] = one.goods_name
                    samp['price_code'] = one.price_code
                    samp['status'] = one.status
                    if one.status == 0:
                        samp['contenter'] = pObj1.name
                        samp['contenting'] = "企划组织"
                    if one.status == 1:
                        samp['contenter'] = pObj3.name
                        samp['contenting'] = "企划用料"
                    if one.status == 2:
                        samp['contenter'] = pObj4.name
                        samp['contenting'] = "企划报价"
                    if one.status == 3:
                        samp['contenter'] = pObj2.name
                        samp['contenting'] = "企划完成"
                    sub =getPlanSub(nid)
                    samp['sub'] = sub
                    temp = {}
                    temp['data'] = samp
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                msg = "未找到对应的企划"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "未找到对应的企划"
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




############################在建企划-企划###############################################

class planPlanerView(APIView):
    # 添加企划
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg =[]
        plan_id = data['plan_id']
        if not isinstance(plan_id,int):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认企划Id正确！"
            samp['key_num'] = "plan_id"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num+1
            valObj = planerOneSerializer(data=done)
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
                            bObj = PlanMaterial.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = PlanMaterial()
                            bObj.create_time = dt
                    except:
                        mid = 0
                        bObj = PlanMaterial()
                        bObj.create_time = dt
                    bObj.status = 0
                    bObj.m_cat = done['m_cat']
                    bObj.m_name = done['m_name']
                    bObj.m_sample = done['m_sample']
                    bObj.complayer = done['complayer']
                    bObj.plan_id = plan_id
                    ppobj = Plan.objects.get(id=plan_id)
                    if ppobj:
                        bObj.edition =ppobj.edition + 1
                        if ppobj.status ==3:
                            if not mid:
                                bObj.is_finish = 1
                        else:
                            bObj.is_finish = 0
                            # 更改企划的状态
                            ppobj.status = 1
                            ppobj.save()
                    else:
                        bObj.flag = 1
                        bObj.is_finish = 0
                        # 更改企划的状态
                        ppobj.status = 1
                        ppobj.save()

                    bObj.create_time = dt
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
                bObj = PlanMaterial.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "在建企划不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class planPlanerOneView(APIView):
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = PlanMaterial.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "在建企划不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


############################在建企划-用料###############################################

class planMaterialView(APIView):
    # 添加企划
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        plan_id = data['plan_id']
        if not isinstance(plan_id, int):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认企划Id正确！"
            samp['key_num'] = "plan_id"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = materialOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    try:
                        mid = done['id']
                        if mid:
                            bObj = PlanMaterial.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = PlanMaterial()
                            bObj.create_time = dt
                    except:
                        mid = 0
                        bObj = PlanMaterial()
                        bObj.create_time = dt
                    bObj.status = 0
                    bObj.m_cat = done['m_cat']
                    bObj.m_name = done['m_name']
                    bObj.m_sample = done['m_sample']
                    bObj.complayer = done['complayer']
                    bObj.sure_m_sample = done['sure_m_sample']
                    bObj.m_unit = done['m_unit']
                    bObj.m_rate = done['m_rate']
                    bObj.m_use = done['m_use']
                    bObj.comments = done['comments']
                    bObj.price = done['price']
                    bObj.total = done['total']
                    bObj.plan_id = plan_id
                    ppobj = Plan.objects.get(id=plan_id)
                    if ppobj:
                        bObj.edition = ppobj.edition + 1
                        if ppobj.status == 3:
                            if not mid:
                                bObj.is_finish = 1
                        else:

                            bObj.is_finish = 0
                            # 更改企划状态
                            ppobj.status = 2
                            ppobj.save()
                    else:
                        bObj.flag = 1
                        bObj.is_finish = 0
                        # 更改企划状态
                        ppobj.status = 2
                        ppobj.save()
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
            msg =l_msg
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class planMaterialOneView(APIView):

    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = PlanMaterial.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划用料删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "在建企划用料不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################在建企划-报价sub###############################################

class planPriceSubView(APIView):
    # 添加企划
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        plan_id = data['plan_id']
        if not isinstance(plan_id, int):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认企划Id正确！"
            samp['key_num'] = "plan_id"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = planpricesubOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    pid = done['id']
                    if pid:
                        bObj = PlanPriceSub.objects.get(id=pid)
                    else:
                        bObj = PlanPriceSub()
                    bObj.status = 0
                    bObj.progrem = done['progrem']
                    bObj.price = done['price']
                    try:
                        bObj.comments = done['comments']
                    except:
                        pass
                    bObj.plan_id = plan_id
                    ppobj = Plan.objects.filter(id=plan_id)
                    if ppobj.count() > 0:
                        bObj.edition = ppobj[0].edition + 1
                        if ppobj[0].status == 3:
                            if not pid:
                                bObj.is_finish = 1
                        else:
                            bObj.is_finish = 0
                    else:
                        bObj.flag = 1
                        bObj.is_finish=0
                    bObj.create_time = dt
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

    # 批量删除用料单位
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = PlanPriceSub.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划项目成本删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "在建企划项目成本不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class planPriceSubOneView(APIView):
    # 删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = PlanPriceSub.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划项目成本删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "在建企划项目成本不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)

############################在建企划-报价###############################################

class planPriceView(APIView):
    # 添加企划报价
    @csrf_exempt
    def post(self, request):
        data = request.query_params
        valObj = planpriceOneSerializer(data=request.query_params)
        dt = datetime.now()
        if valObj.is_valid():
            try:
                # 创建报价
                bObj = PlanPrice()
                bObj.status = 0
                bObj.good_unit = data['good_unit']
                bObj.price_type = data['price_type']
                bObj.plan_id = data['plan_id']
                bObj.price_rate = data['price_rate']
                bObj.gm = data['gm']
                bObj.plan_price = data['plan_price']
                bObj.edition = 1
                bObj.create_time = dt
                bObj.save()
                planOne = Plan.objects.get(id=data['plan_id'])
                # 报价备份
                one = PlanPrice.objects.get(plan_id=data['plan_id'])
                cobj = PlanPriceCopy()
                copyTable(one, cobj)
                #复制用料
                mObj = PlanMaterial.objects.filter(plan_id=data['plan_id'])
                for one in mObj:
                    one.edition = planOne.edition +1
                    one.save()
                    c_pline = PlanMaterialCopy()
                    copyTable(one, c_pline)
                #  报价列表备份
                planbjline = PlanPriceSub.objects.filter(plan_id=data['plan_id'])
                for one in planbjline:
                    one.edition = planOne.edition + 1
                    one.save()
                    c_l_one = PlanPriceSubCopy()
                    copyTable(one, c_l_one)
                planOne.edition = planOne.edition +1
                if planOne.status !=3:
                    planOne.status = 0
                    one.is_finish = 0
                    one.save()
                else:
                    one.is_finish = 1
                    one.save()

                planOne.save()
                msg = "创建在建企划"
                error_code = 0
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "参数校验不通过！"
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


class planPriceOneView(APIView):
    # 设置更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = planpriceOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = PlanPrice.objects.get(id=nid)
            bObj.good_unit = data['good_unit']
            bObj.price_type = data['price_type']
            bObj.plan_id = data['plan_id']
            bObj.price_rate = data['price_rate']
            bObj.gm = data['gm']
            bObj.plan_price = data['plan_price']
            bObj.edition = bObj.edition + 1
            bObj.update_time = dt
            bObj.save()
            planOne = Plan.objects.get(id=data['plan_id'])
            # 报价备份
            one = PlanPrice.objects.get(plan_id=data['plan_id'])
            cobj = PlanPriceCopy()
            copyTable(one, cobj)
            # 复制用料
            mObj = PlanMaterial.objects.filter(plan_id=data['plan_id'])
            for one in mObj:
                one.edition = planOne.edition + 1
                one.save()
                c_pline = PlanMaterialCopy()
                copyTable(one, c_pline)
            #  报价列表备份
            planbjline = PlanPriceSub.objects.filter(plan_id=data['plan_id'])
            for one in planbjline:
                one.edition = planOne.edition + 1
                one.save()
                c_l_one = PlanPriceSubCopy()
                copyTable(one, c_l_one)
            planOne.edition = planOne.edition + 1
            if  planOne.status != 3:
                planOne.status = 0
                planOne.save()
                one.is_finish = 0
                one.save()
            else:
                one.is_finish = 1
                one.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新在建企划成功!",
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

        # 删除用料单位


    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = PlanPrice.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "员工档案不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    #报价历史记录
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        try:
            rObj = PlanPriceCopy.objects.filter(delete_time=None,plan_id=nid)
            pObj = Plan.objects.filter(id=nid)
            result = []
            if pObj.count()>0:
                for one in rObj:
                    samp = {}
                    samp['create_time'] = one.create_time
                    samp['id'] = one.id
                    samp['good_unit'] = one.good_unit
                    samp['edition'] = one.edition
                    samp['price_type'] = one.price_type
                    samp['price_rate'] = one.price_rate
                    samp['plan_price'] = one.plan_price
                    samp['gm'] = one.gm
                    samp['plan_id'] = one.plan_id
                    result.append(samp)
                temp = {}
                tempf={}
                temp["data"] = result
                temp['plan_datetime'] = pObj[0].plan_datetime
                temp['goods_name'] = pObj[0].goods_name
                temp['price_code'] = pObj[0].price_code
                custom = CustomerFiles.objects.get(id=pObj[0].customer_name_id)
                temp['company_name_simple'] = custom.customer_simple_name
                brand = Marks.objects.get(id=pObj[0].brand_id)
                temp['brand'] = brand.brand
                tempf['data'] = temp
                tempf['error_code'] = 0
                tempf['message'] = "成功"
                tempf['request'] = request.method + '  ' + request.get_full_path()

                return Response(tempf)
            else:
                msg = "未找到对应的企划方案"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
        except:
            msg = "未找到对应的企划方案"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)
############################在建企划-历史详情###############################################

class planHistoryOneView(APIView):
    @csrf_exempt
    def get(self, request, nid):
        data = request.query_params
        valObj = planHistoryOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = Plan.objects.filter(delete_time=None, id=nid)
                if rObj.count() > 0:
                    one = rObj[0]
                    samp = {}
                    samp['plan_datetime'] = one.plan_datetime
                    samp['customer_name_id'] = one.customer_name_id
                    cusObj = CustomerFiles.objects.get(id=one.customer_name_id)
                    samp['company_name_simple'] = cusObj.customer_simple_name
                    samp['brand_id'] = one.brand_id
                    bobj = Marks.objects.get(id=one.brand_id)
                    samp['brand'] = bobj.brand
                    samp['plan_org_id'] = one.plan_org_id
                    pObj1 = Archives.objects.get(id=one.plan_org_id)
                    samp['plan_org_er'] = pObj1.name
                    samp['plan_id'] = one.plan_id
                    pObj2 = Archives.objects.get(id=one.plan_id)
                    samp['plan_er'] = pObj2.name
                    samp['material_plan_id'] = one.material_plan_id
                    pObj3 = Archives.objects.get(id=one.material_plan_id)
                    samp['material_plan_er'] = pObj3.name
                    samp['price_id'] = one.price_id
                    pObj4 = Archives.objects.get(id=one.price_id)
                    samp['price_er'] = pObj4.name
                    samp['goods_name'] = one.goods_name
                    samp['price_code'] = one.price_code
                    samp['status'] = one.status
                    sub = getPlanHistory(nid,data['edition'])
                    samp['sub'] = sub
                    tempf = {}
                    tempf['data'] = samp
                    tempf['error_code'] = 0
                    tempf['message'] = "成功"
                    tempf['request'] = request.method + '  ' + request.get_full_path()
                    return Response(tempf)
                msg = "未找到对应的企划"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
            except:
                msg = "未找到对应的企划"
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

############################在建企划-企划档案###############################################
# 获取数组最大值 #
def maxInt(intArray):
    max = 0
    for i in intArray:
        if max < i:
            max = i
    return max

class planOrderView(APIView):
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = planOrderSerializer(data=request.query_params)
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
                status = valObj.data['status'] if valObj.data['status'] is not None else 1
                if status:
                    rObj = PlanOrder.objects.filter(delete_time=None)
                    order_type = valObj.data['order_type'] if valObj.data['order_type'] is not None else 0
                    order_custom = valObj.data['order_custom'] if valObj.data['order_custom'] is not None else ""
                    brand = valObj.data['brand'] if valObj.data['brand'] is not None else ""
                    price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                    dhkhao = valObj.data['dhkhao'] if valObj.data['dhkhao'] is not None else ""
                    is_pushprogram = valObj.data['is_pushprogram'] if valObj.data['is_pushprogram'] is not None else 999
                    is_workprogram = valObj.data['is_workprogram'] if valObj.data['is_workprogram'] is not None else 999
                    is_buyprogram = valObj.data['is_buyprogram'] if valObj.data['is_buyprogram'] is not None else 999
                    is_manage = valObj.data['is_manage'] if valObj.data['is_manage'] is not None else 0
                    is_cloth_sure = valObj.data['is_cloth_sure'] if valObj.data['is_cloth_sure'] is not None else 0
                    if order_type != 0:
                        rObj = rObj.filter(order_type = order_type)
                    if order_custom:
                        rObj = rObj.filter(custom = order_custom)
                    if brand:
                        rObj = rObj.filter(brand = brand)
                    if price_code:
                        rObj = rObj.filter(price_code = price_code)
                    if dhkhao:
                        rObj = rObj.filter(dhkhao = dhkhao)
                    if is_pushprogram !=999:
                        rObj = rObj.filter(is_pushprogram=is_pushprogram)
                    if is_workprogram !=999:
                        rObj = rObj.filter(is_workprogram=is_workprogram)
                    if is_buyprogram !=999:
                        rObj = rObj.filter(is_buyprogram=is_buyprogram)
                    total = rObj.count()
                    if rObj.count() > start:
                        rObj = rObj.all()[start:start+page_size]
                        result = []
                        temp = {}
                        data_n = rObj.values()
                        for p_one in data_n:
                            planObj = Plan.objects.get(id=p_one["plan_id"])
                            p_one["customer_name_id"] = planObj.customer_name_id
                            if is_manage:
                                # 包装
                                pack_num, pack_sure_num = getpackNum(p_one["id"])
                                p_one["pack_num"] = pack_num
                                p_one["pack_sure_num"] = pack_sure_num
                                # 面辅料确认
                                order_cloth_num, order_cloth_sure_num = getClothSureNum(p_one["id"])
                                p_one["order_cloth_num"] = order_cloth_num
                                p_one["order_cloth_sure_num"] = order_cloth_sure_num
                                # 面辅料入库
                                order_cloth_store_num, order_cloth_store_sure_num = getClothInStore(p_one["id"])
                                p_one["order_cloth_store_num"] = order_cloth_store_num
                                p_one["order_cloth_store_sure_num"] = order_cloth_store_sure_num
                                # 成衣样品
                                sample_num, sample_sure_num = getPlanSampleNum(p_one["id"])
                                p_one["sample_num"] = sample_num
                                p_one["sample_sure_num"]= sample_sure_num
                                # 上手倒计时
                                plan_start_date, down_day = getPlanStartdate(p_one["id"])
                                p_one["plan_start_date"] = plan_start_date
                                p_one["down_day"] = down_day
                            if is_cloth_sure:
                                # 包装
                                pack_num, pack_sure_num = getpackNum(p_one["id"])
                                p_one["pack_num"] = pack_num
                                p_one["pack_sure_num"] = pack_sure_num
                                # 面辅料确认
                                order_cloth_num, order_cloth_sure_num = getClothSureNum(p_one["id"])
                                p_one["order_cloth_num"] = order_cloth_num
                                p_one["order_cloth_sure_num"] = order_cloth_sure_num
                                # 面辅料入库
                                order_cloth_store_num, order_cloth_store_sure_num = getClothInStore(p_one["id"])
                                p_one["order_cloth_store_num"] = order_cloth_store_num
                                p_one["order_cloth_store_sure_num"] = order_cloth_store_sure_num
                                # 洗标吊牌
                                drop_lable_num,drop_lable_sure_num = getDropLableNum(p_one["id"])
                                p_one["drop_lable_num"] = drop_lable_num
                                p_one["drop_lable_sure_num"] = drop_lable_sure_num
                                # 注意事项
                                notes_all_num, notes_sure_num = getNotesNum(p_one["id"])
                                p_one["notes_all_num"] = notes_all_num
                                p_one["notes_sure_num"] = notes_sure_num
                                # 上手倒计时
                                plan_start_date, down_day = getPlanStartdate(p_one["id"])
                                p_one["plan_start_date"] = plan_start_date
                                p_one["down_day"] = down_day
                        temp["data"] = data_n
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
                if status==0:
                    rObj = Plan.objects.filter(status=4)
                    customer_name_id = valObj.data['customer_name_id'] if valObj.data[
                                                                              'customer_name_id'] is not None else 0
                    brand_id = valObj.data['brand_id'] if valObj.data['brand_id'] is not None else 0
                    price_code = valObj.data['price_code'] if valObj.data['price_code'] is not None else ""
                    if customer_name_id != 0:
                        rObj = rObj.filter(customer_name_id=customer_name_id)
                    if brand_id:
                        rObj = rObj.filter(brand_id=brand_id)
                    if price_code:
                        rObj = rObj.filter(price_code__contains=price_code)
                    total = rObj.count()
                    if rObj.count() > start:
                        rObj = rObj.all()[start:start + page_size]
                        result = []
                        for one in rObj:
                            samp = {}
                            samp['id'] = one.id
                            samp['create_time'] = one.create_time
                            samp['delete_time'] = one.delete_time
                            samp['plan_datetime'] = one.plan_datetime
                            samp['customer_name_id'] = one.customer_name_id
                            cusObj = CustomerFiles.objects.get(id=one.customer_name_id)
                            samp['company_name_simple'] = cusObj.customer_simple_name
                            samp['brand_id'] = one.brand_id
                            bobj = Marks.objects.get(id=one.brand_id)
                            samp['brand'] = bobj.brand
                            samp['plan_org_post'] = one.plan_org_post
                            samp['plan_org_department'] = one.plan_org_department
                            samp['plan_org_id'] = one.plan_org_id
                            pObj1 = Archives.objects.get(id=one.plan_org_id)
                            samp['plan_org_er'] = pObj1.name
                            samp['plan_department'] = one.plan_department
                            samp['plan_post'] = one.plan_post
                            samp['plan_id'] = one.plan_id
                            pObj2 = Archives.objects.get(id=one.plan_id)
                            samp['plan_er'] = pObj2.name
                            samp['material_plan_department'] = one.material_plan_department
                            samp['material_plan_post'] = one.material_plan_post
                            samp['material_plan_id'] = one.material_plan_id
                            pObj3 = Archives.objects.get(id=one.material_plan_id)
                            samp['material_plan_er'] = pObj3.name
                            samp['price_id'] = one.price_id
                            samp['price_post'] = one.price_post
                            samp['price_department'] = one.price_department
                            pObj4 = Archives.objects.get(id=one.price_id)
                            samp['price_er'] = pObj4.name
                            samp['goods_name'] = one.goods_name
                            samp['price_code'] = one.price_code
                            samp['status'] = one.status
                            if one.status == 0:
                                samp['contenter'] = pObj1.name
                                samp['contenting'] = "企划组织"
                            if one.status == 1:
                                samp['contenter'] = pObj3.name
                                samp['contenting'] = "企划用料"
                            if one.status == 2:
                                samp['contenter'] = pObj4.name
                                samp['contenting'] = "企划报价"
                            if one.status == 3:
                                samp['contenter'] = pObj2.name
                                samp['contenting'] = "企划完成"
                            if one.status == 4:
                                samp['contenter'] = pObj1.name
                                samp['contenting'] = "企划关闭"
                            result.append(samp)
                        temp = {}
                        temp["data"] = result
                        temp['page_size'] = page_size
                        temp['total'] = total
                        temp['error_code'] = 0
                        temp['request'] = request.method + '  ' + request.get_full_path()
                        return Response(temp)
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

    # 添加企划订单
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = planOrderOneSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = planOrderLineOneSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            ##############保存order#############################
            oid = valObj.data['id']
            if oid:
                order = PlanOrder.objects.get(id=oid)
                order.update_time = dt
            else:
                order = PlanOrder()
                order.create_time = dt
            order.dhkhao = data['dhkhao']
            order.department = data['department']
            order.leader = data['leader']
            order.order_type = data['order_type']
            order.plan_id = data['plan_id']
            planObj = Plan.objects.get(id=data['plan_id'])
            cusObj = CustomerFiles.objects.get(id=planObj.customer_name_id)
            bobj = Marks.objects.get(id=planObj.brand_id)
            order.custom = cusObj.customer_simple_name
            order.price_code = planObj.price_code
            if not oid:
                order.is_pushprogram = 0
                order.is_workprogram = 0
                order.is_buyprogram = 0
                order.pushprogram_num =0
                order.workprogram_num = 0
                order.buyprogram_num = 0
            order.plan_status = '企划成功'
            order.workflow = '企划流程..'
            order.order_line_num = len(dataone)
            order.brand = bobj.brand
            order.goods_name = planObj.goods_name
            order.plan_time = planObj.create_time
            order.save()
            if oid:
                orderone =PlanOrder.objects.get(id=oid)
            else:
                orderone = PlanOrder.objects.latest('id')
                # #企划成功
                # planObj.status = 3
                # planObj.save()
            # 企划状态更改
            planObj.status = 3
            planObj.save()
            ##############保存order#############################
            if d_flag == 0:
                contracr_num_all=0
                for done in dataone:
                    try:
                        try:
                            # 生成规则订单号 #
                            timestr = datetime.now().strftime('%Y%m%d')
                            P_timestr = 'P' + str(timestr)
                            snOld = PlanOrderLine.objects.filter(order_sn__contains=P_timestr).values('order_sn')
                            maxNumber = None
                            sn = ""
                            if snOld:
                                snOldInt = []
                                for snOldOne in snOld:
                                    if snOldOne['order_sn'][1:9] == timestr:
                                        snOldInt.append(int(snOldOne['order_sn'][9:]))
                                maxNumber = maxInt(snOldInt)
                                sn = "P" + timestr + "%0*d" % (5, maxNumber + 1)
                            else:
                                sn = "P" + timestr + "00001"
                        except:
                            sn = "P" + timestr + "00001"

                        try:
                            mid = done["id"]
                            if mid:
                                bObj = PlanOrderLine.objects.get(id=mid)
                                bObj.update_time = dt
                            else:
                                bObj = PlanOrderLine()
                                bObj.create_time = dt
                                bObj.order_sn = sn

                        except:
                            bObj = PlanOrderLine()
                            bObj.create_time = dt
                            bObj.order_sn = sn
                        bObj.custom_type = done['custom_type']
                        bObj.order_custom = done['order_custom']
                        bObj.order_type = done['order_type']
                        if done['order_type'] in [1,3]:
                            bObj.price_terms = done['price_terms']
                            bObj.transportation = done['transportation']
                            bObj.pol = done['pol']
                            bObj.exporter_way = done['exporter_way']
                            bObj.warehouse_time = done['warehouse_time']

                        bObj.contract_num = done['contract_num']
                        contracr_num_all += done['contract_num']
                        bObj.short_overflow = done['short_overflow']
                        bObj.pay_way = done['pay_way']
                        bObj.pod = done['pod']
                        if not mid:
                            bObj.is_pushprogram = 0
                            bObj.is_work_progrem = 0
                            bObj.is_buyprogram = 0
                        bObj.inspect_company = done['inspect_company']
                        bObj.delivery_way = done['delivery_way']
                        bObj.send_time = done['send_time']
                        bObj.inspect_time = done['inspect_time']
                        bObj.delivery_time = done['delivery_time']

                        bObj.comments = done['comments']
                        bObj.plan_id = data['plan_id']
                        bObj.order_id = orderone.id
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
                orderone.contract_num = contracr_num_all
                orderone.save()
                msg = "创建在建企划-企划订单"
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

    #订单批量删除
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for nid in ids:
                bObj = PlanOrder.objects.get(id=nid)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
                blObj = PlanOrderLine.objects.filter(order_id=nid)
                for one in blObj:
                    one.delete_time = dt
                    one.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划订单删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "企划订单不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class planOrderOneView(APIView):
    @csrf_exempt
    def delete(self, request, nid):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                one = PlanOrderLine.objects.get(order_id=nid,id=one)
                dt = datetime.now()
                one.delete_time = dt
                one.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "在建企划订单项删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "企划订单列别不存在!",
            error_code = 10020
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
            one = PlanOrder.objects.get(id=nid)
            dt = datetime.now()
            one.is_sure_drop_lable = 1
            one.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "洗标吊牌状态更新成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "企划订单不存在!",
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
        data = request.query_params
        valObj = planOrderGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            try:
                rObj = PlanOrder.objects.filter(delete_time=None, id=nid)
                if rObj.count()>0:
                    one = rObj[0]
                    samp = {}
                    samp['create_time'] = one.create_time
                    samp['id'] = one.id
                    samp['dhkhao'] = one.dhkhao
                    samp['department'] = one.department
                    samp['leader'] = one.lead_id
                    samp['order_type'] = one.order_type
                    samp['custom'] = one.custom
                    samp['price_code'] = one.price_code
                    samp['brand'] = one.brand
                    samp['goods_name'] = one.goods_name
                    samp['plan_time'] = one.plan_time
                    samp['plan_id'] = one.plan_id
                    samp['is_pushprogram'] = one.is_pushprogram
                    samp['is_workprogram'] = one.is_workprogram
                    samp['is_buyprogram'] = one.is_buyprogram
                    samp['pushprogram_num'] = one.pushprogram_num
                    samp['workprogram_num'] = one.workprogram_num
                    samp['buyprogram_num'] = one.buyprogram_num
                    samp['order_line_num'] = one.order_line_num
                    samp['contract_num'] = one.contract_num
                    samp['order_num'] = one.order_num
                    sub =PlanOrderLine.objects.filter(order_id=nid,delete_time=None).values()
                    samp['data'] = sub
                    temp = {}
                    temp["data"] = samp
                    temp['error_code'] = 0
                    temp['message'] = "成功"
                    temp['request'] = request.method + '  ' + request.get_full_path()
                    return Response(temp)
                msg = "未找到对应的企划订单"
                error_code = 10030
                request = request.method + '  ' + request.get_full_path()
                post_result = {
                    "error_code": error_code,
                    "message": msg,
                    "request": request,
                }
                return Response(post_result)
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

############################在建企划-成衣样品###############################################

class planClothSampleView(APIView):
    # 获取成衣样品信息
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = planClothgetSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = PlanClothSampleLine.objects.filter(plan_id=data["plan_id"], delete_time=None)
                planObj = Plan.objects.get(id=data["plan_id"])
                delivery_mode = valObj.data['delivery_mode'] if valObj.data['delivery_mode'] is not None else 0
                department = valObj.data['department'] if valObj.data['department'] is not None else ""
                member = valObj.data['member'] if valObj.data['member'] is not None else ""
                custom_type = valObj.data['custom_type'] if valObj.data['custom_type'] is not None else ""
                custom = valObj.data['custom'] if valObj.data['custom'] is not None else ""
                is_fee = valObj.data['is_fee'] if valObj.data['is_fee'] is not None else 0
                s_id = valObj.data['id'] if valObj.data['id'] is not None else 0
                if delivery_mode:
                    rObj = rObj.filter(delivery_mode__contains=delivery_mode)
                if department:
                    rObj = rObj.filter(department__contains=department)
                if member:
                    rObj = rObj.filter(member__contains=member)
                if custom_type:
                    rObj = rObj.filter(custom_type__contains=custom_type)
                if custom:
                    rObj = rObj.filter(custom__contains=custom)
                if is_fee:
                    rObj = rObj.filter(is_fee=is_fee)
                if s_id:
                    rObj = rObj.filter(id=s_id)
                temp = {}
                temp["data"] = rObj.values()
                custom = CustomerFiles.objects.get(id=planObj.customer_name_id)
                temp['customer_simple_name'] = custom.customer_simple_name
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的成衣样品信息"
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

    # 添加企划成衣样品
    @csrf_exempt
    def post(self, request):
        data = request.data
        valObj = planClothOneSerializer(data=request.data)
        if valObj.is_valid():
            #################校验数据################################
            d_flag = 0
            d_num = 0
            l_msg = []
            dataone = data['data']
            for done in dataone:
                d_num = d_num + 1
                valObjline = planClothlineSerializer(data=done)
                if not valObjline.is_valid():
                    d_flag = 1
                    samp = {}
                    samp['msg'] = valObjline.errors
                    samp['key_num'] = d_num
                    l_msg.append(samp)
            #################校验数据################################
            dt = datetime.now()
            if d_flag == 0:
                for done in dataone:
                    try:
                        valObjOne = planClothlineSerializer(data=done)
                        if valObjOne.is_valid():
                            try:
                                mid = done["id"]
                                if mid:
                                    bObj = PlanClothSampleLine.objects.get(id=mid)
                                    bObj.update_time = dt
                                else:
                                    bObj = PlanClothSampleLine()
                                    bObj.create_time = dt

                            except:
                                bObj = PlanClothSampleLine()
                                bObj.create_time = dt
                            bObj.delivery_mode = valObjOne.data['delivery_mode']
                            if valObjOne.data['delivery_mode'] ==1:
                                bObj.department = valObjOne.data['department']
                                bObj.member = valObjOne.data['member']
                            else:
                                bObj.custom_type = valObjOne.data['custom_type']
                                bObj.custom = valObjOne.data['custom']
                            bObj.required_time = done['required_time']
                            bObj.sample_type = done['sample_type']
                            bObj.delivery_member = done['delivery_member']
                            bObj.send_custom = done['send_custom']
                            bObj.countdown = done['countdown']
                            bObj.send_num = done['send_num']
                            bObj.send_time = done['send_time']
                            bObj.is_fee = done['is_fee']
                            bObj.is_pay = done['is_pay']
                            bObj.file_url = done['file_url']
                            bObj.status = 0
                            bObj.pcs_id = 0
                            bObj.plan_id = valObj.data['plan_id']
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
                msg = "创建在建企划-成衣样品"
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

    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = PlanClothSampleLine.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "成衣样品删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "成衣样品不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class planClothSampleOneView(APIView):
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = PlanClothSampleLine.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "成衣样品删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "成衣样品不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################在建企划-成衣样品colorSpecs###############################################

class planColorSpecsView(APIView):
    # 获取成衣样品数量信息
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = planColorSpecsGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = PlanClothSampleNumber.objects.filter(pcsl_id=data["pcsl_id"], delete_time=None)
                s_id = valObj.data['id'] if valObj.data['id'] is not None else 0
                if s_id:
                    rObj = rObj.filter(id=s_id)
                temp = {}
                temp["data"] = rObj.values()
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的成衣样品数量信息"
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

    # 添加成衣样品信息
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg =[]
        pcsl_id = data['pcsl_id']
        if not isinstance(pcsl_id,int):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认成衣样品样品类型Id正确！"
            samp['key_num'] = "pcsl_id"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num+1
            valObj = planColorSpecsSerializer(data=done)
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
                            bObj = PlanClothSampleNumber.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = PlanClothSampleNumber()
                            bObj.create_time = dt
                    except:
                        bObj = PlanClothSampleNumber()
                        bObj.create_time = dt
                    bObj.status = 0
                    bObj.sub_color_id = done['sub_color_id']
                    bObj.sub_color_name = done['sub_color_name']
                    bObj.sub_specs_id = done['sub_specs_id']
                    bObj.sub_specs_name = done['sub_specs_name']
                    bObj.num = done['num']
                    bObj.pcsl_id = pcsl_id
                    bObj.save()
                except:
                    msg = "未找到成衣样品"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            l_list  = PlanClothSampleNumber.objects.filter(pcsl_id = pcsl_id)
            send_num = 0
            for one in l_list:
                send_num =send_num+one.num
            pcslOne = PlanClothSampleLine.objects.get(id=pcsl_id)
            pcslOne.send_num = send_num
            pcslOne.save()
            msg = "创建在建企划-成衣样品数量"
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
                bObj = PlanClothSampleNumber.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "成衣样品数量信息删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "成衣样品数量信息不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class planColorSpecsOneView(APIView):
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = PlanClothSampleNumber.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "成衣样品数量信息删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "成衣样品数量信息不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################在建企划-式样书###############################################

class sampleCatalogueView(APIView):
    # 获取式样书
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = sampleCataGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = SampleCatalogue.objects.filter(plan_id=data["plan_id"], delete_time=None)
                s_id = valObj.data['id'] if valObj.data['id'] is not None else 0
                if s_id:
                    rObj = rObj.filter(id=s_id)
                temp = {}
                temp["data"] = rObj.values()
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的式样书"
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

    # 添加样式书
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg =[]
        plan_id = data['plan_id']
        if not isinstance(plan_id,int):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认企划Id正确！"
            samp['key_num'] = "plan_id"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num+1
            valObj = sampleCatalogueOneSerializer(data=done)
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
                            bObj = SampleCatalogue.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = SampleCatalogue()
                            bObj.create_time = dt
                    except:
                        bObj = SampleCatalogue()
                        bObj.create_time = dt
                    bObj.status = 1
                    bObj.samp_name = done['samp_name']
                    bObj.samp_time = done['samp_time']
                    bObj.samp_file_url = done['samp_file_url']
                    bObj.plan_id = plan_id
                    bObj.save()
                except:
                    msg = "式样书参数校验失败！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "创建更新在建企划-式样书"
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

    #批量删除
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids =data['ids']
            for one in ids:
                bObj = SampleCatalogue.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "式样书删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "式样书不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class sampleCatalogueOneView(APIView):
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = SampleCatalogue.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "式样书删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "式样书不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################在建企划-制版###############################################

class plateMakingView(APIView):
    # 获取式样书
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = plateMakingGetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            result = []
            try:
                rObj = PlateMaking.objects.filter(plan_id=data["plan_id"], delete_time=None)
                s_id = valObj.data['id'] if valObj.data['id'] is not None else 0
                if s_id:
                    rObj = rObj.filter(id=s_id)
                temp = {}
                temp["data"] = rObj.values()
                temp['error_code'] = 0
                temp['message'] = "成功"
                temp['request'] = request.method + '  ' + request.get_full_path()
                return Response(temp)

            except:
                msg = "未找到对应的制版"
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

    # 添加样式书
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        plan_id = data['plan_id']
        if not isinstance(plan_id, int):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认企划Id正确！"
            samp['key_num'] = "plan_id"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = plateMakingOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    try:
                        mid = done["id"]
                        if mid:
                            bObj = PlateMaking.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = PlateMaking()
                            bObj.create_time = dt
                    except:
                        bObj = PlateMaking()
                        bObj.create_time = dt
                    bObj.status = 1
                    bObj.plate_name = done['plate_name']
                    bObj.plate_time = done['plate_time']
                    bObj.plate_file_url = done['plate_file_url']
                    bObj.plan_id = plan_id
                    bObj.save()
                except:
                    msg = "制版参数校验失败！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "创建在建企划-制版"
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

    #批量删除
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = PlateMaking.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "制版删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "制版不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)


class plateMakingOneView(APIView):

    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = PlateMaking.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "制版删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "制版不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

############################预警方式###############################################
class warmSetView(APIView):
    @csrf_exempt
    def get(self, request):
        result = []
        try:
            rObj = BaseWarm.objects.filter(delete_time=None).order_by('weight')
            for one in rObj:
                temp = {}
                if one.active == 1:
                    temp['active'] = True
                else:
                    temp['active'] = False
                temp["warm_type"] = one.warm_type
                temp["id"] = one.id
                temp['warm_time_num'] = one.warm_time_num
                temp['warm_num_name'] = one.warm_num_name
                temp['warm_name'] = one.warm_name
                temp['weight'] = one.weight
                result.append(temp)
            samp = {}
            samp["data"] = result
            samp['error_code'] = 0
            samp['message'] = "成功"
            samp['request'] = request.method + '  ' + request.get_full_path()
            return Response(samp)
        except:
            msg = "未找预警信息"
            error_code = 10030
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

    # 添加预警方式
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认企划Id正确！"
            samp['key_num'] = "name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = setWarmSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    try:
                        mid = done["id"]
                        if mid:
                            bObj = BaseWarm.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            warmobj = BaseWarm.objects.filter(
                                warm_type=done['warm_type'],
                                warm_time_num=done['warm_time_num'],
                                warm_name=done['warm_name'],
                                delete_time=None
                            )
                            if warmobj.count() > 0:
                                msg = "预警信息已经存在"
                                error_code = 400
                                request = request.method + '  ' + request.get_full_path()
                                post_result = {
                                    "error_code": error_code,
                                    "message": msg,
                                    "request": request,
                                }
                                return Response(post_result)
                            bObj = BaseWarm()
                            bObj.create_time = dt
                    except:
                        bObj = BaseWarm()
                        bObj.create_time = dt
                    num = BaseWarm.objects.all().count() + 1
                    bObj.warm_type = done['warm_type']
                    bObj.warm_time_num = done['warm_time_num']
                    bObj.warm_num_name = done['warm_num_name']
                    bObj.warm_name = done['warm_name']
                    bObj.active = done['active']
                    bObj.create_time = dt
                    if not mid:
                        bObj.weight = num
                    bObj.save()
                except:
                    msg = "参数校验失败！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            msg = "创建修改预警信息"
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
                bObj = BaseWarm.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "预警方式删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "预警方式不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class warmSetOneView(APIView):
    #订单类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = setWarmSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = BaseWarm.objects.get(id=nid)
            bObj.active = data['active']
            bObj.warm_type = data['warm_type']
            bObj.warm_time_num = data['warm_time_num']
            bObj.warm_num_name = data['warm_num_name']
            bObj.warm_name = data['warm_name']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新预警消息成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = BaseWarm.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "预警信息删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "预警信息不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class warmSetSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = BaseWarm.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = BaseWarm.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": " 预警信息排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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


############################短溢装###############################################
class shortShipView(APIView):
    # 样品类型名称
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = shortShipSerializer(data=request.query_params)
        result = []
        if valObj.is_valid():
            result = []
            try:
                active = valObj.data['active'] if valObj.data['active'] is not None else 2
                short_num = valObj.data['short_num'] if valObj.data['short_num'] is not None else 0
                rObj = ShortShip.objects.filter(delete_time=None).order_by('weight')
                if active !=2:
                    rObj = rObj.filter(active = active)
                if short_num:
                    rObj = rObj.filter(short_num = short_num)
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["short_num"] = one.short_num
                    temp["defalut"] = one.defalut
                    temp['id'] = one.id
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的短溢装"
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

    # 添加用料单位
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = shortShipOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    shortship = ShortShip.objects.filter(
                        short_num=done['short_num']
                    )
                    if shortship.count()>0:
                        d_flag = 1
                        samp = {}
                        samp['msg'] = "短溢装已经存在"
                        samp['key_num'] = done['short_num']
                        l_msg.append(samp)
                    else:
                        mid = done["id"]
                        if mid:
                            bObj = ShortShip.objects.get(id=mid)
                            bObj.update_time = dt
                        else:
                            bObj = ShortShip()
                            bObj.create_time = dt
                        num = ShortShip.objects.all().count() + 1
                        bObj.short_num = done['short_num']
                        bObj.defalut = done['defalut']
                        bObj.active = done['active']
                        bObj.create_time = dt
                        if not mid:
                            bObj.weight = num
                        bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建/更新短溢装信息"
            else:
                msg = l_msg
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
        # 批量删除用料单位

    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = ShortShip.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "短溢装删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "短溢装不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)

class shortShipOneView(APIView):
    #订单类型更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = shortShipOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = ShortShip.objects.get(id=nid)
            bObj.active = data['active']
            bObj.short_num = data['short_num']
            bObj.defalut = data['defalut']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新短溢装成功!",
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
    #删除用料单位
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = ShortShip.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "短溢装删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "短溢装不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class shortShipSortView(APIView):
    #样品类型名称排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = ShortShip.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = ShortShip.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "短溢装排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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

############################订单日期设置###############################################
class orderDateSetView(APIView):
    # 样品类型名称
    @csrf_exempt
    def get(self, request):
        data = request.query_params
        valObj = orderDateSetSerializer(data=request.query_params)
        result = []
        if valObj.is_valid():
            result = []
            try:
                mid = valObj.data['id'] if valObj.data['id'] is not None else 0
                rObj = OrderDateSet.objects.filter(delete_time=None).order_by('weight')
                if mid:
                    rObj = rObj.filter(id = mid)
                for one in rObj:
                    temp = {}
                    if one.active == 1:
                        temp['active'] = True
                    else:
                        temp['active'] = False
                    temp["port_type"] = one.port_type
                    temp["send_num"] = one.send_num
                    temp["in_num"] = one.in_num
                    temp["takeover_num"] = one.takeover_num
                    temp['id'] = one.id
                    temp['weight'] = one.weight
                    result.append(temp)
                return Response(result)
            except:
                msg = "未找到对应的时间日期设置"
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

    # 添加短溢装
    @csrf_exempt
    def post(self, request):
        data = request.data
        #################校验数据################################
        d_flag = 0
        d_num = 0
        l_msg = []
        api_name = data['name']
        if not isinstance(api_name, str):
            d_flag = 1
            samp = {}
            samp['msg'] = "请确认api接口名称！"
            samp['key_num'] = "api_name"
            l_msg.append(samp)
        data = data['data']
        for done in data:
            d_num = d_num + 1
            valObj = orderDateSetOneSerializer(data=done)
            if not valObj.is_valid():
                d_flag = 1
                samp = {}
                samp['msg'] = valObj.errors
                samp['key_num'] = d_num
                l_msg.append(samp)
        #################校验数据################################
        dt = datetime.now()
        if d_flag == 0:
            for done in data:
                try:
                    mid = done["id"]
                    if mid:
                        bObj = OrderDateSet.objects.get(id=mid)
                        bObj.update_time = dt
                    else:
                        bObj = OrderDateSet()
                        bObj.create_time = dt
                    num = OrderDateSet.objects.all().count() + 1
                    bObj.port_type = done['port_type']
                    bObj.send_num = done['send_num']
                    bObj.in_num = done['in_num']
                    bObj.takeover_num = done['takeover_num']
                    bObj.active = done['active']
                    if not mid:
                        bObj.weight = num
                    bObj.save()
                except:
                    msg = "参数校验不通过！"
                    error_code = 10030
                    request = request.method + '  ' + request.get_full_path()
                    post_result = {
                        "error_code": error_code,
                        "message": msg,
                        "request": request,
                    }
                    return Response(post_result)
            if d_flag == 0:
                msg = "创建/更新订单时间日期设置信息"
            else:
                msg = l_msg
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
    # 批量删除短溢装
    @csrf_exempt
    def delete(self, request):
        try:
            data = request.data
            ids = data['ids']
            for one in ids:
                bObj = OrderDateSet.objects.get(id=one)
                dt = datetime.now()
                bObj.delete_time = dt
                bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "短溢装删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "订单时间日期设置不存在!"
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request
            }
            return Response(post_result)

class orderDateSetOneView(APIView):
    #短溢装更新-active
    @csrf_exempt
    def put(self, request, nid):
        data = request.query_params
        valObj = orderDateSetOneSerializer(data=request.query_params)
        if valObj.is_valid():
            dt = datetime.now()
            bObj = OrderDateSet.objects.get(id=nid)
            bObj.active = data['active']
            bObj.port_type = data['port_type']
            bObj.send_num = data['send_num']
            bObj.in_num = data['in_num']
            bObj.takeover_num = data['takeover_num']
            bObj.update_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "更新订单时间日期成功!",
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
    #删除短溢装
    @csrf_exempt
    def delete(self, request, nid):
        try:
            bObj = OrderDateSet.objects.get(id=nid)
            dt = datetime.now()
            bObj.delete_time = dt
            bObj.save()
            # 返回数据
            request = request.method + '  ' + request.get_full_path()
            error_code = 0
            post_result = {
                "error_code": error_code,
                "message": "订单日期时间设置删除成功!",
                "request": request,
            }
            return Response(post_result)
        except:
            msg = "订单时间日期设置不存在!",
            error_code = 10020
            request = request.method + '  ' + request.get_full_path()
            post_result = {
                "error_code": error_code,
                "message": msg,
                "request": request,
            }
            return Response(post_result)

class orderDateSetSortView(APIView):
    #短溢装排序
    def put(self,request,bid):
        data = request.query_params
        valObj = BasicSortSerializer(data=request.query_params)
        if valObj.is_valid():
            obj = OrderDateSet.objects.all()
            offset = int(data['offset'])
            bid = bid
            begin_weight = OrderDateSet.objects.get(id=bid).weight
            result = Msort(obj, offset, bid, begin_weight)
            if result:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "订单时间日期设置排序成功!",
                    "request": request,
                }
                return Response(post_result)
            else:
                # 返回数据
                request = request.method + '  ' + request.get_full_path()
                error_code = 0
                post_result = {
                    "error_code": error_code,
                    "message": "偏移量超出范围!",
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


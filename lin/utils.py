# -*- coding:UTF-8 -*-
import logging
import types

import django
from django.db import models
# from django.utils import simplejson as json
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

def clearData(s):
    dirty_stuff = ["\"", "\\", "/", "*", "'", "=", "-", "#", ";", "<", ">", "+", "%"]
    dirty_stuff.extend(["select","SELECT","DROP","drop","delete","DELETE","update","UPDATE","INESRT","insert","CREATE","create"])
    for stuff in dirty_stuff:
        s = s.replace(stuff,"")
    return s


def percentage(count, total):
    if total == 0:
        return "0%"

    rate = float(count) / float(total)
    percent = int(rate * 100)
    return "%d%%" % percent


def json_encode(data):
    """
    The main issues with django's default json serializer is that properties that
    had been added to a object dynamically are being ignored (and it also has
    problems with some models).
    """

    def _any(data):
        ret = None
        if type(data) is list:
            ret = _list(data)
        elif type(data) is dict:
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = str(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        elif isinstance(data, ModelState):
            ret = None
        elif isinstance(data, datetime):
            ret = data.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(data, date):
            ret = data.strftime('%Y-%m-%d')
        # elif isinstance(data, django.db.models.fields.related.RelatedManager):
        #    ret = _list(data.all())
        else:
            ret = data
        return ret

    def _model(data):
        # ret = {}
        # # If we only have a model, we only want to encode the fields.
        # for f in data._meta.fields:
        #     ret[f.attname] = _any(getattr(data, f.attname))
        # # And additionally encode arbitrary properties that had been added.
        # fields = dir(data.__class__) + ret.keys()
        # add_ons = [k for k in dir(data) if k not in fields]
        # for k in add_ons:
        #     ret[k] = _any(getattr(data, k))
        ret = model_to_dict(data)
        ret = _dict(ret)
        return ret

    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret

    def _dict(data):
        ret = {}
        for k, v in data.items():
            ret[k] = _any(v)
        return ret

    ret = _any(data)
    return json.dumps(ret,ensure_ascii=False)

@csrf_exempt
def upload_file(request):
    ret = "0"
    # tmpIm = cStringIO.StringIO(request.FILES['resource'])
    uploadedFileURI = ''  # 上传后文件路径
    uploadedFileName = ''  # 上传后文件名
    if request.method == 'POST':
        msg = "form.is_valid() =false"
        f = request.FILES['resource']
        uploadedFileName = str("newpic" + datetime.now().strftime("%Y%m%d%H%M%S") + os.path.splitext(f.name)[1])
        destinationPath = str(settings.MEDIA_ROOT + "temp/" + uploadedFileName)
        destination = open(destinationPath, 'wb')
        uploadedFileURI = str(settings.DOMAIN_URL + 'upload/temp/' + uploadedFileName)
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        msg = "destination.close()"
    post_result = "{\"ret\":" + ret + ", \"message\":\"" + msg + "\",\"fileuri\":\"" + uploadedFileURI + "\", \"filename\":\"" + uploadedFileName + "\", \"destinationPath\":\"" + destinationPath +"\"}"
    return HttpResponse(post_result)


class k8Logger(object):
    @staticmethod
    def basicConfig():
        # 判断当天日志文件是否存在，如果存在就保存至今日的日志文件，否则。。。
        strNow = datetime.now().strftime("%Y%m%d")
        logFilePath = settings.PROJECT_PATH + '/log/log' + strNow + '.log'
        if not os.path.isfile(logFilePath):
            logging.basicConfig(filename=logFilePath, level=logging.INFO)  # StreamHandler

    @staticmethod
    def info(logMessage):
        k8Logger.basicConfig()
        strNow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info('--logtime:' + strNow + '--' + logMessage)

    @staticmethod
    def error(logMessage):
        k8Logger.basicConfig()
        strNow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error('--logtime:' + strNow + '--' + logMessage)




class CreateQrCode(object):
    """创建二维码图片"""

    def __init__(self,hrefstr,headhref):
        """初始化配置信息"""
        self.version = 1
        self.error_correction = qrcode.constants.ERROR_CORRECT_H
        self.box_size = 10
        self.border = 1
        self.hrefstr= hrefstr
        self.headhref=headhref

    def getImg(self):
        """下载微信头像"""
        url = self.headhref
        uploadedFileName = str("wxheadimg" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randrange(0, 100)))
        destination = str(settings.MEDIA_ROOT + "headimg/" + uploadedFileName)
        #保存文件时候注意类型要匹配，如要保存的图片为jpg，则打开的文件的名称必须是jpg格式，否则会产生无效图片
        conn = urllib.urlopen(url).read()
        f = open(destination,'wb')
        f.write(conn)
        f.close()
        return destination

    def freeCollarCode(self,merchantMouldImg):
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(self.hrefstr)
        qr.make(fit=True)
        img = qr.make_image()
        img = img.resize((194,194), Image.ANTIALIAS)
        backImg = Image.open(merchantMouldImg)
        backImg.paste(img, (43, 803))
        uploadedFileName = str("free" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randrange(0, 100))+'.jpg')
        destination = str(settings.MEDIA_ROOT + "freeCollar/" + uploadedFileName)
        backImg.save(destination)
        return uploadedFileName

    def onlyCode(self):
        """二维码图片"""
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(self.hrefstr)
        qr.make(fit=True)
        img = qr.make_image()
        uploadedFileName = str("QRCode" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randrange(0, 1000))+'.jpg')
        destination = str(settings.MEDIA_ROOT + "QRCode/" + uploadedFileName)
        img.save(destination,'JPEG')
        return uploadedFileName

    def groupSnCode(self,groupSn,name,price,pic):
        """二维码图片"""
        #字体加载
        font_price = ImageFont.truetype("/usr/share/fonts/truetype/simsun.ttf",30)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/simsun.ttf",20)
        #商品图片加载
        good_pic = Image.open(settings.MEDIA_ROOT + "goods/" + pic)
        good_pic = good_pic.resize((160,160),Image.ANTIALIAS)
        #二维码加载
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(self.hrefstr)
        qr.make(fit=True)
        code = qr.make_image()
        code = code.resize((280,280),Image.ANTIALIAS)
        #图片粘贴
        img = Image.new("RGBA",(480,640),(255,255,255))
        img.paste(good_pic, (40, 40))
        img.paste(code, (100, 340))
        #图片加字
        draw = ImageDraw.Draw(img)
        lineCount = 0
        while(len(name) > 0):
            #为防止商品名太长,每行写10个字符
            text = name[:10]
            draw.text((240,60 + lineCount * 40), text,(0,0,0),font=font_name)
            name = name[len(text):]
            lineCount += 1
        draw.text( (240,60 + lineCount * 40), price,(0,0,0),font=font_price)
        uploadedFileName = str("QRCode" + groupSn +'.jpg')
        destination = str(settings.MEDIA_ROOT + "QRCode/" + uploadedFileName)
        img.save(destination,'JPEG')
        return uploadedFileName

    def memInfoCode(self):
        """个人信息二维码图片"""
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(self.hrefstr)
        qr.make(fit=True)
        img = qr.make_image()
        uploadedFileName = str("QRMember" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randrange(0, 100))+'.jpg')
        destination = str(settings.MEDIA_ROOT + "QRCode/" + uploadedFileName)
        img.save(destination,'JPEG')
        return uploadedFileName


    def imgCode(self):
        """加图片的二维码图片"""
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(self.hrefstr)
        qr.make(fit=True)

        img = qr.make_image()
        img = img.convert("RGB")
        herdimg=self.getImg()
        icon = Image.open(herdimg)

        img_w, img_h = img.size
        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)

        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)

        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        img.paste(icon, (w, h))
        uploadedFileName = str("QRCode" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randrange(0, 100))+'.jpg')
        destination = str(settings.MEDIA_ROOT + "QRCode/" + uploadedFileName)
        img.save(destination,'JPEG')
        return uploadedFileName

@csrf_exempt
def uploadDescImg(request):
    if request.method == 'POST':
        try:
            callback = request.GET.get('CKEditorFuncNum')
            f = request.FILES['upload']
            uploadedFileName = str("newpic" + datetime.now().strftime("%Y%m%d%H%M%S") + os.path.splitext(f.name)[1])
            destination = open(str(settings.MEDIA_ROOT + "productLine/productstory/" + uploadedFileName), 'wb')
            uploadedFileURI = str(settings.DOMAIN_URL + 'upload/productLine/productstory/' + uploadedFileName)
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            retval = "<script>window.parent.CKEDITOR.tools.callFunction("+callback+",'"+'/upload/productLine/productstory/' + uploadedFileName+"', '');</script>"
            return HttpResponse("<script>window.parent.CKEDITOR.tools.callFunction("+callback+",'"+'/upload/productLine/productstory/' + uploadedFileName+"', '');</script>")
        except:
            callback = request.GET.get('CKEditorFuncNum')
            return HttpResponse("<script>window.parent.CKEDITOR.tools.callFunction(" + callback
                    + ",''," + "'上传失败');</script>")


def Msort(obj, offset, bid, begin_weight):
    end = begin_weight + offset
    if end < 0:
        return False
    if offset > 0:
        q = obj.filter(weight__gt=begin_weight, weight__lte=end)
        for one in q:
            one.weight = one.weight - 1
            one.save()

    if offset < 0:
        q = obj.filter(Q(weight__lt=begin_weight)|Q(weight__gte=end))
        for one in q:
            one.weight = one.weight + 1
            one.save()
    one = obj.get(id=bid)
    one.weight = end
    one.save()
    return True

#复制表
def copyTable(oldOne,newOne):
    dict = model_to_dict(oldOne)
    newOne.__dict__.update(dict)
    # newOne = copy.deepcopy(oldOne)
    newOne.id=None
    newOne.old_id=oldOne.id
    newOne.save()

def vsTable(oneList,twoAll):
    oneList = oneList.values()
    twoAll = twoAll
    for one in oneList:
        two = twoAll.filter(old_id=one["id"])
        if two.count()>0:
            two_p = two.filter(edition=one["edition"])
            if two_p.count()>0:
                one["diff"] = []
            else:
                edition=one["edition"]-1
                two = two.filter(edition=edition)
                if two.count()>0:
                    dic_two = model_to_dict(two[0])
                    diff=one.keys()
                    diff_val = [k for k in diff if one[k] !=dic_two[k]]
                    one["diff"] = diff_val
                else:
                    one["diff"]=[]
        else:
            one["diff"] = [k for k in one.keys()]
    return oneList


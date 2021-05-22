# -*- coding: utf-8 -*-
from django.urls import path
from django.conf.urls import url

from order import views
urlpatterns = [

    url('^showOutStock$', views.showOutStockView.as_view()),
    url('^showOutStock/(?P<nid>\d+)', views.showOutStockOneView.as_view()),

    url('^factoryMake$', views.factoryMakeView.as_view()),
    url('^factoryMake/(?P<nid>\d+)', views.factoryMakeOneView.as_view()),

    url('^machining$', views.machiningView.as_view()),
    url('^machining/(?P<nid>\d+)', views.machiningOneView.as_view()),

    url('^orderCloth$', views.orderClothView.as_view()),
    url('^orderCloth/(?P<nid>\d+)', views.orderClothOneView.as_view()),

    url('^management$', views.managementView.as_view()),
    url('^management/(?P<nid>\d+)', views.managementOneView.as_view()),

    url('^orderNotes$', views.orderNotesView.as_view()),
    url('^orderNotes/(?P<nid>\d+)', views.orderNotesOneView.as_view()),

    url('^shipment$', views.shipmentView.as_view()),
    url('^shipment/(?P<nid>\d+)', views.shipmentOneView.as_view()),

    url('^packing$', views.packingView.as_view()),
    url('^packing/(?P<nid>\d+)', views.packingOneView.as_view()),

    url('^packingLine$', views.packingLineView.as_view()),
    url('^packingLine/(?P<nid>\d+)', views.packingLineOneView.as_view()),

    url('^shipmentSure$', views.shipmentSureView.as_view()),
    url('^shipmentSure/(?P<nid>\d+)', views.shipmentSureOneView.as_view()),

    url('^purchasRecords$', views.purchasRecordsView.as_view()),
    url('^purchasRecords/(?P<nid>\d+)', views.purchasRecordsOneView.as_view()),

    url('^shipmentInStock$', views.shipmentInStockView.as_view()),
    url('^shipmentInStock/(?P<nid>\d+)', views.shipmentInStockOneView.as_view()),
    #生产准备
    url('^productReady$', views.productReadyView.as_view()),
    url('^makeinReady$', views.makeinReadyView.as_view()),

    url('^submission$', views.submissionView.as_view()),
    url('^submission/(?P<nid>\d+)', views.submissionOneView.as_view()),

    url('^submissionInfo$', views.submissionInfoView.as_view()),
    url('^submissionInfo/(?P<nid>\d+)', views.submissionInfoOneView.as_view()),

    url('^indicateDate$', views.indicateDateView.as_view()),

    url('^colorSizeData$', views.colorSizeDataView.as_view()),
    url('^colorSizeData/(?P<nid>\d+)', views.colorSizeDataOneView.as_view()),




]
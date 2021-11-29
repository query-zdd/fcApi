# -*- coding: utf-8 -*-
from django.urls import path
from django.conf.urls import url
from order import views
urlpatterns = [

    url('^showOutStock$', views.showOutStockView.as_view()),
    url('^showOutStock/(?P<nid>\d+)', views.showOutStockOneView.as_view()),

    url('^showFXOutStock/(?P<nid>\d+)', views.showFXOutStockOneView.as_view()),

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

    url('^orderNotesOther$', views.orderNotesOtherView.as_view()),
    url('^orderNotesOther/(?P<nid>\d+)', views.orderNotesOtherOneView.as_view()),

    url('^shipment$', views.shipmentView.as_view()),
    url('^shipment/(?P<nid>\d+)', views.shipmentOneView.as_view()),

    url('^packing$', views.packingView.as_view()),
    url('^packing/(?P<nid>\d+)', views.packingOneView.as_view()),

    url('^packingLine$', views.packingLineView.as_view()),
    url('^packingLine/(?P<nid>\d+)', views.packingLineOneView.as_view()),

    url('^shipmentSure$', views.shipmentSureView.as_view()),
    url('^shipmentSure/(?P<nid>\d+)', views.shipmentSureOneView.as_view()),

    url('^shipmentSure/drop$', views.dropView.as_view()),
    url('^shipmentSure/drop/(?P<nid>\d+)', views.dropOneView.as_view()),

    url('^shipmentSure/dropLable$', views.dropLableView.as_view()),
    url('^shipmentSure/dropLable/(?P<nid>\d+)', views.dropLableOneView.as_view()),

    url('^purchasRecords$', views.purchasRecordsView.as_view()),
    url('^purchasRecords/(?P<nid>\d+)', views.purchasRecordsOneView.as_view()),

    url('^shipmentInStock$', views.shipmentInStockView.as_view()),
    url('^shipmentInStock/(?P<nid>\d+)', views.shipmentInStockOneView.as_view()),
    #生产准备
    url('^productReady$', views.productReadyView.as_view()),
    url('^productReady/(?P<nid>\d+)$', views.productReadyOneView.as_view()),
    url('^makeinReady$', views.makeinReadyView.as_view()),

    url('^submission$', views.submissionView.as_view()),
    url('^submission/(?P<nid>\d+)', views.submissionOneView.as_view()),

    url('^submissionInfo$', views.submissionInfoView.as_view()),
    url('^submissionInfo/(?P<nid>\d+)', views.submissionInfoOneView.as_view()),

    url('^indicateDate$', views.indicateDateView.as_view()),

    url('^colorSizeData$', views.colorSizeDataView.as_view()),
    url('^colorSizeData/(?P<nid>\d+)', views.colorSizeDataOneView.as_view()),

    url('^reightSpace$', views.reightSpaceView.as_view()),
    url('^reightSpace/(?P<nid>\d+)', views.reightSpaceOneView.as_view()),

    url('^exportCustomsDeclaration$', views.exportCustomsDeclarationView.as_view()),
    url('^exportClothSample/(?P<nid>\d+)', views.exportClothSampleView.as_view()),

    url('^inportCustomsDeclaration$', views.inportCustomsDeclarationView.as_view()),

    url('^makeFactoryInspect$', views.makeFactoryInspectView.as_view()),
    url('^makeFactoryInspect/(?P<nid>\d+)', views.makeFactoryInspectOneView.as_view()),

    url('^PackInfo$', views.PackInfoView.as_view()),
    url('^PackInfo/(?P<nid>\d+)', views.PackInfoOneView.as_view()),

    url('^Bquality$', views.BqualityView.as_view()),
    url('^Bquality/(?P<nid>\d+)', views.BqualityOneView.as_view()),

    url('^showContract$', views.showContractView.as_view()),
    url('^showContract/(?P<nid>\d+)', views.showContractOneView.as_view()),

    url('^exportFactoryInspect$', views.exportFactoryInspectView.as_view()),
    url('^exportFactoryInspect/(?P<nid>\d+)', views.exportFactoryInspectOneView.as_view()),

    url('^orderAccounts$', views.orderAccountsView.as_view()),
    url('^orderAccounts/(?P<nid>\d+)', views.orderAccountsOneView.as_view()),
    url('^orderOtherAccounts$', views.orderOtherAccountsView.as_view()),
    url('^orderOtherAccounts/(?P<nid>\d+)', views.orderOtherAccountsOneView.as_view()),
    url('^orderInAccounts$', views.orderInAccountsView.as_view()),
    url('^orderInAccounts/(?P<nid>\d+)', views.orderInAccountsOneView.as_view()),
    # 明细
    url('^orderInALLAccounts$', views.orderInAllAccountsView.as_view()),


    url('^productAccounts$', views.productAccountsView.as_view()),
    url('^productAccounts/(?P<nid>\d+)', views.productAccountsOneView.as_view()),

    url('^productMakeAccounts$', views.productMakeAccountsView.as_view()),
    url('^productMakeAccounts/(?P<nid>\d+)', views.productMakeAccountsOneView.as_view()),

    url('^productOtherAccounts$', views.productOtherAccountsView.as_view()),
    url('^productOtherAccounts/(?P<nid>\d+)', views.productOtherAccountsOneView.as_view()),

    url('^productInAccounts$', views.productInAccountsView.as_view()),
    url('^productInAccounts/(?P<nid>\d+)', views.productInAccountsOneView.as_view()),

    url('^productInALLAccounts$', views.productInALLAccountsView.as_view()),

    url('^productPayAccounts$', views.productPayAccountsView.as_view()),
    url('^productPayAccounts/(?P<nid>\d+)', views.productPayAccountsOneView.as_view()),

    url('^sampleAccounts$', views.sampleAccountsView.as_view()),

    url('^sampleAccountsTools$', views.sampleAccountsToolsView.as_view()),
    url('^sampleAccountsTools/(?P<nid>\d+)', views.sampleAccountsToolsOneView.as_view()),

    url('^sampleOtherAccounts$', views.sampleOtherAccountsView.as_view()),
    url('^sampleOtherAccounts/(?P<nid>\d+)', views.sampleOtherAccountsOneView.as_view()),

    url('^samplePayNumAccounts$', views.samplePayNumAccountsView.as_view()),
    url('^samplePayNumAccounts/(?P<nid>\d+)', views.samplePayNumAccountsOneView.as_view()),

    url('^sampleInAccounts$', views.sampleInAccountsView.as_view()),
    url('^sampleInAccounts/(?P<nid>\d+)', views.sampleInAccountsOneView.as_view()),

    url('^sampleInAllAccounts$', views.sampleInAllAccountsView.as_view()),

    # 发票管理
    url('^showReceipt$', views.showReceiptView.as_view()),
    url('^saveReceipt$', views.saveReceiptView.as_view()),
    # 档案
    url('^showReceiptBuyData$', views.showReceiptBuyDataView.as_view()),
    url('^showReceiptMakeData$', views.showReceiptMakeDataView.as_view()),
    url('^showReceiptOtherData$', views.showReceiptOtherDataView.as_view()),
    url('^showReceiptSampData$', views.showReceiptSampDataView.as_view()),
    # 采购发票
    url('^getBuyReceipt/(?P<nid>\d+)', views.getBuyReceiptOneView.as_view()),
    #加工费
    url('^getMakeReceipt/(?P<nid>\d+)', views.getMakeReceiptOneView.as_view()),
    #其他项目
    url('^getOtherReceipt/(?P<nid>\d+)', views.getOtherReceiptOneView.as_view()),
    # 成衣样品
    url('^getSampReceipt/(?P<nid>\d+)', views.getSampReceiptOneView.as_view()),
    # 结汇管理
    url('^showSurrender$', views.showSurrenderView.as_view()),
    # 工资管理
    url('^showSalaryStandard$', views.showSalaryStandardView.as_view()),
    url('^showMouthSalary$', views.showMouthSalaryView.as_view()),
    url('^showSalaryInfo$', views.showSalaryInfoView.as_view()),

    # 订单分析
    url('^showOrderStatic$', views.showOrderStaticView.as_view()),
    #生产汇总分析
    url('^showFXFactoryMake/(?P<nid>\d+)', views.showFXFactoryMakeOneView.as_view()),
    #生产用料
    url('^shipmentFXCloth/(?P<nid>\d+)', views.shipmentFXSureOneView.as_view()),

    url('^newOtherAccounts$', views.newOtherAccountsView.as_view()),
    url('^newOtherAccounts/(?P<nid>\d+)$', views.newOtherOneAccountsView.as_view()),

    # 用料成本
    url('^shipmentFXINCloth/(?P<nid>\d+)', views.shipmentFXInSureOneView.as_view()),

]
# -*- coding: utf-8 -*-
from django.urls import path
from django.conf.urls import url


from lin import views
urlpatterns = [
    #文件上传-获取token
    url('^file/image/token$', views.fileTokenView.as_view()),
    #文件上传-获取路径
    url('^file/callback$', views.fileCallbackView.as_view()),

    url('^basic$', views.basicView.as_view()),
    url('^basic/(?P<nid>\d+)', views.basicUpdateView.as_view()),
    url('^basic/sort/(?P<bid>\d+)', views.basicSortView.as_view()),
    url('^sample/type$', views.sampleTypeView.as_view()),
    url('^sample/type/(?P<nid>\d+)', views.sampleOneView.as_view()),
    url('^sample/type/sort/(?P<bid>\d+)', views.sampleSortView.as_view()),
    url('^harbour$', views.harbourView.as_view()),
    url('^harbour/(?P<nid>\d+)', views.houbourOneView.as_view()),
    url('^harbour/sort/(?P<bid>\d+)', views.harbourSortView.as_view()),

    url('^size$', views.sizeView.as_view()),
    url('^size/(?P<nid>\d+)', views.sizeOneView.as_view()),
    url('^size/sort/(?P<bid>\d+)', views.sizeSortView.as_view()),

    url('^size/sub_size$', views.subsizeView.as_view()),
    url('^size/sub_size/(?P<nid>\d+)', views.subsizeOneView.as_view()),
    url('^size/sub_size/sort/(?P<bid>\d+)', views.subsizeSortView.as_view()),

    url('^receiving$', views.receivingView.as_view()),
    url('^receiving/(?P<nid>\d+)', views.receivingOneView.as_view()),
    url('^receiving/sort/(?P<bid>\d+)', views.receivingSortView.as_view()),

    url('^receiving/warehouse$', views.warehouseView.as_view()),
    url('^receiving/warehouse/(?P<nid>\d+)', views.warehouseOneView.as_view()),
    url('^receiving/warehouse/sort/(?P<bid>\d+)', views.warehouseSortView.as_view()),

    #面辅料类别设置
    url('^cloth/cloth_class$', views.cloth_classView.as_view()),
    url('^cloth/cloth_class/(?P<nid>\d+)', views.cloth_classOneView.as_view()),
    url('^cloth/cloth_class/sort/(?P<bid>\d+)', views.cloth_classSortView.as_view()),
    #面辅料名称设置
    url('^cloth$', views.clothView.as_view()),
    url('^cloth/(?P<nid>\d+)', views.clothOneView.as_view()),
    url('^cloth/sort/(?P<bid>\d+)', views.clothSortView.as_view()),
    #面辅料成分设置
    url('^cloth/material$', views.clothmaterialView.as_view()),
    url('^cloth/material/(?P<nid>\d+)', views.clothmaterialOneView.as_view()),
    url('^cloth/material/sort/(?P<bid>\d+)', views.clothmaterialSortView.as_view()),
    # 面辅料颜色设置
    url('^colour$', views.colourView.as_view()),
    url('^colour/(?P<nid>\d+)', views.colourOneView.as_view()),
    url('^colour/sort/(?P<bid>\d+)', views.colourSortView.as_view()),
    # 面辅料子颜色设置
    url('^colour/sub_colour$', views.sub_colourView.as_view()),
    url('^colour/sub_colour/(?P<nid>\d+)', views.sub_colourOneView.as_view()),
    url('^colour/sub_colour/sort/(?P<bid>\d+)', views.sub_colourSortView.as_view()),
    # 面辅料规格
    url('^specs$', views.specsView.as_view()),
    url('^specs/(?P<nid>\d+)', views.specsOneView.as_view()),
    url('^specs/sort/(?P<bid>\d+)', views.specsSortView.as_view()),
    # 面辅料 子规格
    url('^specs/sub_specs$', views.sub_specsView.as_view()),
    url('^specs/sub_specs/(?P<nid>\d+)', views.sub_specsOneView.as_view()),
    url('^specs/sub_specs/sort/(?P<bid>\d+)', views.sub_specsSortView.as_view()),


    #订单号设置
    url('^single/set$', views.singlesetView.as_view()),
    url('^single/set/(?P<nid>\d+)', views.singlesetOneView.as_view()),
    #发票号设置
    url('^invoice$', views.invoiceView.as_view()),
    url('^invoice/(?P<nid>\d+)', views.invoiceOneView.as_view()),
    #客户 类型设置
    url('^customer/type$', views.customerTypeView.as_view()),
    url('^customer/type/(?P<nid>\d+)', views.customerTypeOneView.as_view()),
    url('^customer/type/sort/(?P<bid>\d+)', views.customerTypeSortView.as_view()),

    #客户 档案设置
    url('^customer_files$', views.customer_filesView.as_view()),
    url('^customer_files/(?P<nid>\d+)', views.customer_filesOneView.as_view()),

    #客户 联系方式设置
    url('^contact$', views.contactView.as_view()),
    url('^contact/(?P<nid>\d+)', views.contactOneView.as_view()),

    #客户 名片设置
    url('^customer_files/namecard/(?P<nid>\d+)', views.namecardOneView.as_view()),
    #客户  唛头设置
    url('^customer_files/namecard/marks/(?P<nid>\d+)', views.marksOneView.as_view()),

    #客户 开票设置
    url('^customer_files/company$', views.customerTypeView.as_view()),
    url('^customer_files/company/(?P<nid>\d+)', views.customerTypeOneView.as_view()),
    url('^customer_files/company/sort/(?P<bid>\d+)', views.customerTypeSortView.as_view()),

    #部门设置
    url('^department/post$', views.departmentPostView.as_view()),
    url('^department/post/(?P<nid>\d+)', views.departmentPostOneView.as_view()),
    url('^department/post/sort/(?P<bid>\d+)', views.departmentPostSortView.as_view()),

    #部门设置
    url('^department$', views.departmentView.as_view()),
    url('^department/(?P<nid>\d+)', views.departmentOneView.as_view()),
    url('^department/sort/(?P<bid>\d+)', views.departmentSortView.as_view()),

    #工号设置
    url('^job_number$', views.job_numberView.as_view()),
    url('^job_number/(?P<nid>\d+)', views.job_numberOneView.as_view()),
    #员工资料
    url('^template/(?P<nid>\d+)', views.templateOneView.as_view()),
    url('^template/sort/(?P<bid>\d+)', views.templateSortView.as_view()),

    #入离职档案设置
    url('^archive$', views.archiveView.as_view()),
    url('^getArchive$', views.getArchiveView.as_view()),
    url('^archive/(?P<nid>\d+)', views.archiveOneView.as_view()),

    #入离职档案设置
    url('^archiveInFile$', views.archiveInFile.as_view()),
    url('^archiveInFile/(?P<nid>\d+)', views.archiveInFileOneView.as_view()),

    #注意事项-类别设置
    url('^category$', views.categoryView.as_view()),
    url('^category/(?P<nid>\d+)', views.categoryOneView.as_view()),
    url('^category/sort/(?P<bid>\d+)', views.categorySortView.as_view()),

    # 注意事项
    url('^notes$', views.notesView.as_view()),
    url('^notes/(?P<nid>\d+)', views.notesOneView.as_view()),
    url('^notes/sort/(?P<bid>\d+)', views.notesSortView.as_view()),

    #其他注意事项-类别设置
    url('^category_set$', views.category_setView.as_view()),
    url('^category_set/(?P<nid>\d+)', views.category_setOneView.as_view()),
    url('^category_set/sort/(?P<bid>\d+)', views.category_setSortView.as_view()),

    #其他注意事项-类别分类
    url('^other_category$', views.other_categoryView.as_view()),
    url('^other_category/(?P<nid>\d+)', views.other_categoryOneView.as_view()),
    url('^other_category/sort/(?P<bid>\d+)', views.other_categorySortView.as_view()),

    #其他注意事项-类别子分类
    url('^other_category/sub_category$', views.sub_categoryView.as_view()),
    url('^other_category/sub_category/(?P<nid>\d+)', views.sub_categoryOneView.as_view()),

    # 注意事项
    url('^other_notes$', views.other_notesView.as_view()),
    url('^other_notes/(?P<nid>\d+)', views.other_notesOneView.as_view()),
    url('^other_notes/sort/(?P<bid>\d+)', views.other_notesSortView.as_view()),

    # 在建企划
    url('^plan$', views.planView.as_view()),
    url('^plan/(?P<nid>\d+)', views.planOneView.as_view()),

    # 在建企划-企划
    url('^plan/planer$', views.planPlanerView.as_view()),
    url('^plan/planer/(?P<nid>\d+)', views.planPlanerOneView.as_view()),

    # 在建企划-用料
    url('^plan/material$', views.planMaterialView.as_view()),
    url('^plan/material/(?P<nid>\d+)', views.planMaterialOneView.as_view()),

    # 在建企划-成本核算
    url('^plan/priceSub$', views.planPriceSubView.as_view()),
    url('^plan/priceSub/(?P<nid>\d+)', views.planPriceSubOneView.as_view()),

    # 在建企划-报价
    url('^plan/price$', views.planPriceView.as_view()),
    url('^plan/price/(?P<nid>\d+)', views.planPriceOneView.as_view()),

    # 在建企划-成衣样品
    url('^plan/planClothSample$', views.planClothSampleView.as_view()),
    url('^plan/planClothSample/(?P<nid>\d+)', views.planClothSampleOneView.as_view()),

    # 在建企划-成衣样品
    url('^plan/planClothSample/colorSpecs$', views.planColorSpecsView.as_view()),
    url('^plan/planClothSample/colorSpecs/(?P<nid>\d+)', views.planColorSpecsOneView.as_view()),

    # 在建企划-式样书
    url('^plan/sampleCatalogue$', views.sampleCatalogueView.as_view()),
    url('^plan/sampleCatalogue/(?P<nid>\d+)', views.sampleCatalogueOneView.as_view()),

    # 在建企划-制版
    url('^plan/plateMaking$', views.plateMakingView.as_view()),
    url('^plan/plateMaking/(?P<nid>\d+)', views.plateMakingOneView.as_view()),

    # 在建企划-历史记录
    url('^plan/planHistory/(?P<nid>\d+)', views.planHistoryOneView.as_view()),

    # 在建企划-录入订单
    url('^plan/planOrder$', views.planOrderView.as_view()),
    url('^plan/planOrder/(?P<nid>\d+)', views.planOrderOneView.as_view()),

    #预警设置
    url('^warmSet$', views.warmSetView.as_view()),
    url('^warmSet/(?P<nid>\d+)', views.warmSetOneView.as_view()),
    url('^warmSet/sort/(?P<bid>\d+)', views.warmSetSortView.as_view()),
    # 短溢装
    url('^shortShip$', views.shortShipView.as_view()),
    url('^shortShip/(?P<nid>\d+)', views.shortShipOneView.as_view()),
    url('^shortShip/sort/(?P<bid>\d+)', views.shortShipSortView.as_view()),
    #订单时间设置
    url('^orderDateSet$', views.orderDateSetView.as_view()),
    url('^orderDateSet/(?P<nid>\d+)', views.orderDateSetOneView.as_view()),
    url('^orderDateSet/sort/(?P<bid>\d+)', views.orderDateSetSortView.as_view()),
    # 财务分析
    url('^basic/financeCat$', views.financeCatView.as_view()),

    url('^financeMouth$', views.financeMouthView.as_view()),

    url('^financeStatic$', views.financeStaticView.as_view()),

    #权限管理
    url('^showAuthority$', views.showAuthorityView.as_view()),

    url('^showAuthorityRole$', views.showAuthorityRoleView.as_view()),
    url('^showAuthorityRole/sort/(?P<bid>\d+)', views.showAuthorityRoleSortView.as_view()),
    # 账户管理
    url('^showRegisterRole$', views.showRegisterRoleView.as_view()),
    url('^showRegisterRole/sort/(?P<bid>\d+)', views.showRegisterRoleSortView.as_view()),
    #账户登录
    url('^showLogin$', views.showLoginView.as_view()),
    # 社保基数
    url('^showSociInsurance$', views.showSociInsuranceView.as_view()),
    url('^showSociInsurance/sort/(?P<bid>\d+)', views.showSociInsuranceSortView.as_view()),

    # 社保基数
    url('^showSurplu$', views.showSurPluView.as_view()),
    url('^showSurplu/sort/(?P<bid>\d+)', views.showSurPluSortView.as_view()),

]
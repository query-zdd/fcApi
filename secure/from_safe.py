from rest_framework import serializers
from lin.models import *
#文件上传
class UploadTokenSerializer(serializers.Serializer):
    bucket = serializers.CharField(error_messages={'required':'存储空间名称不能为空'})

#订单类型
class BasicTypeSerializer(serializers.Serializer):
    type_name = serializers.CharField(error_messages={'required':'订单类型不能为空'})

#订单类型update
class BasicTypeUpdateSerializer(serializers.Serializer):
    active = serializers.CharField(error_messages={'required':'数据更新参数为空！'})

#订单类型update
class BasicInsertSerializer(serializers.Serializer):
    basic_value_en = serializers.CharField(error_messages={'required':'必须传入基础资料英文！'})
    basic_value_zh = serializers.CharField(error_messages={'required': '必须传入基础资料信息！'})
    active = serializers.CharField(error_messages={'required': '数据参数不可为空！'})
    type_name = serializers.CharField(error_messages={'required': '必须传入基础类型名称！'})

#订单类型update
class BasicSortSerializer(serializers.Serializer):
    offset = serializers.IntegerField(error_messages={'required': '必须传入偏移量'})

# 样品类型名称
class SampleInsertSerializer(serializers.Serializer):
    sample_type_zh = serializers.CharField(error_messages={'required':'必须传入样品类型信息(中文)！'})
    sample_type_en = serializers.CharField(error_messages={'required': '必须传入样品类型信息(英文)！'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})
    balance = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

#港口类型
class harborSerializer(serializers.Serializer):
    harbour_type = serializers.CharField(default="")

#商品尺码
class goodsSizeSerializer(serializers.Serializer):
    goods_size = serializers.CharField(default="")

class harborOneSerializer(serializers.Serializer):
    harbour_zh = serializers.CharField(error_messages={'required':'必须传入港口名称(中文)'})
    harbour_en = serializers.CharField(error_messages={'required': '必须传入港口名称(英文)！'})
    harbour_type = serializers.CharField(error_messages={'required': '目的港起运港'})
    order_id = serializers.IntegerField(error_messages={'required': '必须传入贸易类型！'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class sizeOneSerializer(serializers.Serializer):
    goods_size = serializers.CharField(error_messages={'required':'必须传入商品尺码'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class subsizeOneSerializer(serializers.Serializer):
    size = serializers.CharField(error_messages={'required': '必须传入子尺码名称'})
    goods_size = serializers.CharField(error_messages={'required':'商品尺码不能为空'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class receivingOneSerializer(serializers.Serializer):
    method_name = serializers.CharField(error_messages={'required': '收货方式不能为空'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class warehouseSerializer(serializers.Serializer):
    warehouse_name = serializers.CharField(error_messages={'required': '必须传仓库分类名称'})
    method_id = serializers.CharField(error_messages={'required': '收货方式不能为空'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class singleSetSerializer(serializers.Serializer):
    type_name = serializers.CharField(error_messages={'required': '订单号不能为空'})

class singleSetOneSerializer(serializers.Serializer):
    type_name = serializers.CharField(error_messages={'required': '类型不能为空'})
    prefix_name = serializers.CharField(error_messages={'required': '前置不可为空'})
    time_type = serializers.CharField(error_messages={'required': '时间不可为空'})
    customer_type_id = serializers.IntegerField(error_messages={'required': '客户类型不能为空！'})
    code_sign_start = serializers.CharField(error_messages={'required': '数据参数不可为空'})
    code_number_start = serializers.CharField(error_messages={'required': '数据参数不可为空'})

class customerTypeSerializer(serializers.Serializer):
    active = serializers.IntegerField(default=2)
    selected_single = serializers.IntegerField(default=2)
    selected_invoice = serializers.IntegerField(default=2)

class customerOneSerializer(serializers.Serializer):
    customer_type = serializers.CharField(error_messages={'required': '类型不能为空'})
    active = serializers.CharField(error_messages={'required': '数据参数不可为空'})

class invoiceSerializer(serializers.Serializer):
    prefix_type = serializers.IntegerField(default=0)
    prefix_name = serializers.CharField(default="")
    code_number_start = serializers.CharField(default="")

class customer_filesSerializer(serializers.Serializer):
    type_id = serializers.CharField(error_messages={'required': '类型不能为空'})
    customer_simple_name = serializers.CharField(default="")
    order_type = serializers.CharField(default=0)
    brand = serializers.CharField(default="")
    active = serializers.CharField(default=2)

class customer_filesOneSerializer(serializers.Serializer):
    type_id = serializers.CharField(error_messages={'required': '类型不能为空'})
    customer_full_name = serializers.CharField(error_messages={'required': '类型不能为空'})
    customer_simple_name = serializers.CharField(error_messages={'required': '类型不能为空'})
    office_phone = serializers.CharField(error_messages={'required': '类型不能为空'})
    fax_number = serializers.CharField(error_messages={'required': '类型不能为空'})
    active = serializers.CharField(error_messages={'required': '类型不能为空'})

class contactOneSerializer(serializers.Serializer):
    customer_id = serializers.CharField(error_messages={'required': '必须传入客户档案ID'})
    department_name = serializers.CharField(error_messages={'required': '参数不能为空'})
    post_name = serializers.CharField(error_messages={'required': '参数不能为空'})
    contact_name = serializers.CharField(error_messages={'required': '参数不能为空'})
    phone = serializers.CharField(error_messages={'required': '参数不能为空'})
    email = serializers.CharField(error_messages={'required': '参数不能为空'})
    remarks = serializers.CharField(error_messages={'required': '参数不能为空'})

class namecardOneSerializer(serializers.Serializer):
    language = serializers.CharField(error_messages={'required': '必须传入语言名称'})
    company_name = serializers.CharField(error_messages={'required': '必须传入公司全称'})
    company_name_simple = serializers.CharField(error_messages={'required': '必须传入公司简称'})
    country = serializers.CharField(error_messages={'required': '必须传入国家名称'})
    company_address = serializers.CharField(error_messages={'required': '必须传入公司地址'})

class marksOneSerializer(serializers.Serializer):
    brand = serializers.CharField(error_messages={'required': '必须传入经营品牌'})
    brand_url = serializers.CharField(error_messages={'required': '必须传入唛头资源'})
    active = serializers.CharField(error_messages={'required': '参数不能为空'})

class cloth_classSerializer(serializers.Serializer):
    active = serializers.IntegerField(default=2)
    cloth_class_name = serializers.CharField(default="")

class cloth_classOneSerializer(serializers.Serializer):
    active = serializers.IntegerField(default=2)
    cloth_class_name = serializers.CharField(error_messages={'required': '面辅料类别名称不能为空'})

class clothSerializer(serializers.Serializer):
    class_id = serializers.IntegerField(default=0)
    cloth = serializers.CharField(default="")

class clothOneSerializer(serializers.Serializer):
    cloth = serializers.CharField(error_messages={'required': '必须传入面料名'})
    class_id = serializers.CharField(error_messages={'required': '面辅料类别名称不能为空'})
    active = serializers.CharField(error_messages={'required': '参数不能为空'})
    checked = serializers.CharField(error_messages={'required': '参数不能为空'})
class clothMaterialOneSerializer(serializers.Serializer):
    material = serializers.CharField(error_messages={'required': '必须传入面辅料材料'})
    cloth_id = serializers.CharField(error_messages={'required': '必须传入面料ID'})
    active = serializers.IntegerField(error_messages={'required': '参数不能为空'})

class clothMaterialUOneSerializer(serializers.Serializer):
    material = serializers.CharField(error_messages={'required': '必须传入面辅料材料'})
    active = serializers.IntegerField(error_messages={'required': '参数不能为空'})

class colourSerializer(serializers.Serializer):
    colour_name = serializers.CharField(default="")

class colourOneSerializer(serializers.Serializer):
    colour_name = serializers.CharField(error_messages={'required': '必须传入面辅料材料'})
    active = serializers.IntegerField(error_messages={'required': '参数不能为空'})

class subcolourOneSerializer(serializers.Serializer):
    sub_colour_name = serializers.CharField(error_messages={'required': '必须传子颜色名称'})
    colour_id = serializers.CharField(error_messages={'required': '面辅料颜色不能为空'})
    active = serializers.IntegerField(error_messages={'required': '参数不能为空'})

class subcolourUOneSerializer(serializers.Serializer):
    sub_colour_name = serializers.CharField(error_messages={'required': '必须传子颜色名称'})
    active = serializers.IntegerField(error_messages={'required': '参数不能为空'})

class specsSerializer(serializers.Serializer):
    specs_name = serializers.CharField(default="")
    specs_unit = serializers.CharField(default="")

class specsOneSerializer(serializers.Serializer):
    specs_name = serializers.CharField(error_messages={'required': '面辅料规格不能为空'})
    specs_unit = serializers.CharField(error_messages={'required': '面辅料规格单位不能为空'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class subspecsSerializer(serializers.Serializer):
    sub_specs_name = serializers.CharField(error_messages={'required': '必须传子规格名称'})
    specs_id = serializers.CharField(error_messages={'required': '面辅料规格不能为空'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class subspecsUSerializer(serializers.Serializer):
    sub_specs_name = serializers.CharField(error_messages={'required': '必须传子规格名称'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class departmentSerializer(serializers.Serializer):
    department_name = serializers.CharField(default="")

class jobnumberSerializer(serializers.Serializer):
    sort_type = serializers.IntegerField(default=0)

class departmentOneSerializer(serializers.Serializer):
    department_name = serializers.CharField(error_messages={'required': '必须传入部门名称'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class postOneSerializer(serializers.Serializer):
    post_name = serializers.CharField(error_messages={'required': '必须传岗位名称'})
    department_id = serializers.CharField(error_messages={'required': '部门不能为空'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class postUOneSerializer(serializers.Serializer):
    post_name = serializers.CharField(error_messages={'required': '必须传岗位名称'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class jobnumSerializer(serializers.Serializer):
    sort_type = serializers.CharField(default=0)

class jobnumOneSerializer(serializers.Serializer):
    end_number = serializers.CharField(error_messages={'required': '工号结束不能为空'})
    start_number = serializers.CharField(error_messages={'required': '工号起始号码不能为空'})
    sort_type = serializers.CharField(error_messages={'required': '排序方式不能为空'})

class templateOneSerializer(serializers.Serializer):
    name = serializers.CharField(error_messages={'required': '必须传入资料模版名称'})
    template_url = serializers.CharField(error_messages={'required': '必须传入模版资源路径'})
    required = serializers.ChoiceField(default=1, choices=[(0, 'not_null'), (1, 'allow_null')])
    active = serializers.ChoiceField(default=1, choices=[(0, 'inactive'), (1, 'active')])

class archivesSerializer(serializers.Serializer):
    status = serializers.ChoiceField(default=2, choices=[(0, 'on_job'), (1, 'departure'),(2,'all')])
    department_id = serializers.IntegerField(default=0)
    post_id = serializers.IntegerField(default=0)
    name = serializers.CharField(default="")

class archivesFileOneSerializer(serializers.Serializer):
    type_id = serializers.IntegerField(error_messages={'required': '必须传入入离职信息id'})
    archives_id = serializers.IntegerField(error_messages={'required': '必须传入员工id'})

class archivesOneEditSerializer(serializers.Serializer):
    leave_time = serializers.CharField(default="")
    birthday_day = serializers.IntegerField(default=0)
    birthday_mouth = serializers.IntegerField(default=0)
    type_id = serializers.IntegerField(default=0)


class archivesFileSerializer(serializers.Serializer):
    name = serializers.CharField(error_messages={'required': '必须传入资料模版名称'})
    template_url = serializers.CharField(error_messages={'required': '必须传入模版资源路径'})
    type_id = serializers.IntegerField(error_messages={'required': '必须传入模版类型'})
    archives_id = serializers.IntegerField(error_messages={'required': '必须传入员工的id'})
    template_id = serializers.IntegerField(error_messages={'required': '必须传入员工资料模板的id'})

class archivesOneSerializer(serializers.Serializer):
    name = serializers.CharField(error_messages={'required': '必须传入姓名'})
    gender = serializers.ChoiceField(default=0,choices=[(0,'male'),(1,'female')])
    birthday = serializers.CharField(error_messages={'required': '此参数不可为空'})
    department_id = serializers.CharField(error_messages={'required': '必须传入部门ID'})
    post_id = serializers.CharField(error_messages={'required': '必须传入岗位ID'})
    phone = serializers.CharField(error_messages={'required': '必须传入联系方式'})
    emergency_contact = serializers.CharField(error_messages={'required': '必须传入紧急联系人'})
    emergency_phone = serializers.CharField(error_messages={'required': '必须传入紧急联系方式'})
    due_to_time = serializers.CharField(error_messages={'required': '必须传入到期时间'})
    enter_time = serializers.CharField(error_messages={'required': '必须传入入职时间'})
    leave_time = serializers.CharField(error_messages={'required': '必须传入离职时间'})

class categorySerializer(serializers.Serializer):
    cloth_class_id = serializers.IntegerField(default=0)
    cloth_id = serializers.IntegerField(default=0)

class categoryNoteGetSerializer(serializers.Serializer):
    cloth_class_id = serializers.IntegerField(default=0)
    cloth_id = serializers.IntegerField(default=0)
    cloth_category_id = serializers.IntegerField(default=0)

class othercategoryNoteGetSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(default=0)
    sub_category_id = serializers.IntegerField(default=0)
    otehr_cat_set_id = serializers.IntegerField(default=0)

class categoryOneSerializer(serializers.Serializer):
    category_name = serializers.CharField(error_messages={'required': '必须传入注意事项类别'})
    active = serializers.ChoiceField(default=0,choices=[(0,'inactive'),(1,'active')])
    cloth_id = serializers.CharField(error_messages={'required': '必须传入面料ID'})

class categoryUOneSerializer(serializers.Serializer):
    category_name = serializers.CharField(error_messages={'required': '必须传入注意事项类别'})
    active = serializers.ChoiceField(default=0,choices=[(0,'inactive'),(1,'active')])

class notesOneSerializer(serializers.Serializer):
    notes_name = serializers.CharField(error_messages={'required': '必须传入注意事项内容'})
    active = serializers.ChoiceField(default=0,choices=[(0,'inactive'),(1,'active')])
    category_id = serializers.CharField(error_messages={'required': '必须传入注意事项类别ID'})

class notesUOneSerializer(serializers.Serializer):
    notes_name = serializers.CharField(error_messages={'required': '必须传入注意事项内容'})
    active = serializers.ChoiceField(default=0,choices=[(0,'inactive'),(1,'active')])

class othercategorySerializer(serializers.Serializer):
    category_id = serializers.IntegerField(default=0)
    sub_category_id = serializers.IntegerField(default=0)

class ocategorySerializer(serializers.Serializer):
    category_id = serializers.IntegerField(default=0)
    sub_category_id = serializers.IntegerField(default=0)

class ocategoryOneSerializer(serializers.Serializer):
    category_setting_name = serializers.IntegerField(error_messages={'required': '必须传入其他注意事项类别'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])
    sub_category_id = serializers.CharField(error_messages={'required': '必须传入类别名称ID'})

class ocategoryUOneSerializer(serializers.Serializer):
    category_setting_name = serializers.IntegerField(error_messages={'required': '必须传入其他注意事项类别'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class othercategerSerializer(serializers.Serializer):
    category_name = serializers.CharField(default="")

class othercategerOneSerializer(serializers.Serializer):
    category_name = serializers.CharField(error_messages={'required': '必须传入类别分类'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class ocategorysubOneSerializer(serializers.Serializer):
    sub_name = serializers.CharField(error_messages={'required': '必须传入类别名称'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])
    category_id = serializers.IntegerField(error_messages={'required': '类别分类不能为空'})

class ocategorysubUOneSerializer(serializers.Serializer):
    sub_name = serializers.IntegerField(error_messages={'required': '必须传入类别名称'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class otherNotesSerializer(serializers.Serializer):
    notes_name = serializers.IntegerField(error_messages={'required': '必须传入其他注意事项内容'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])
    category_setting_id = serializers.CharField(error_messages={'required': '必须传入其他注意事项类别ID'})

class otherNotesUSerializer(serializers.Serializer):
    notes_name = serializers.IntegerField(error_messages={'required': '必须传入其他注意事项内容'})
    active = serializers.ChoiceField(default=0, choices=[(0, 'inactive'), (1, 'active')])

class planSerializer(serializers.Serializer):
    customer_name_id = serializers.IntegerField(default=0)
    brand_id = serializers.IntegerField(default=0)
    price_code = serializers.CharField(default="")
    start_time = serializers.DateTimeField(default=0)
    end_time = serializers.DateTimeField(default=0)
    page_size = serializers.IntegerField(default=10)
    page = serializers.IntegerField(default=1)
    status = serializers.IntegerField(default=0)

class planOneStopSerializer(serializers.Serializer):
    status = serializers.IntegerField(default=4)

class planOneSerializer(serializers.Serializer):
    brand_id = serializers.IntegerField(error_messages={'required': '必须传入品牌Id'})
    customer_name_id = serializers.IntegerField(error_messages={'required': '必须传入客户Id'})
    plan_id = serializers.IntegerField(error_messages={'required': '必须传入企划发起人id'})
    plan_org_id = serializers.IntegerField(error_messages={'required': '必须传入企划组织人id'})
    material_plan_id = serializers.IntegerField(error_messages={'required': '必须传入用料制版人id'})
    price_id = serializers.IntegerField(error_messages={'required': '必须传入企划报价人id'})
    goods_name = serializers.CharField(error_messages={'required': '必须传入品名'})
    price_code = serializers.CharField(error_messages={'required': '必须传入打样款号'})
    plan_datetime = serializers.CharField(error_messages={'required': '企划日期不可为空'})
    plan_department = serializers.CharField(error_messages={'required': '企划发起人部门不可为空'})
    plan_post = serializers.CharField(error_messages={'required': '企划发起人岗位不可为空'})
    plan_org_department = serializers.CharField(error_messages={'required': '企划组织部门不可为空'})
    plan_org_post = serializers.CharField(error_messages={'required': '企划组织岗位不可为空'})
    material_plan_department = serializers.CharField(error_messages={'required': '用料制版部门不可为空'})
    material_plan_post = serializers.CharField(error_messages={'required': '用料制版岗位不可为空'})
    price_post = serializers.CharField(error_messages={'required': '企划报价岗位不可为空'})
    price_department = serializers.CharField(error_messages={'required': '企划报价部门不可为空'})

class planerOneSerializer(serializers.Serializer):
    m_cat = serializers.CharField(error_messages={'required': '必须传入面辅料类别'})
    m_name = serializers.CharField(error_messages={'required': '必须传入面辅料名称'})
    # m_sample = serializers.CharField(error_messages={'required': '必须传入面辅料规格'})
    # complayer = serializers.CharField(error_messages={'required': '必须传入供应商'})
    id = serializers.IntegerField(default=0)


class materialOneSerializer(serializers.Serializer):
    m_cat = serializers.CharField(error_messages={'required': '必须传入面辅料类别'})
    m_name = serializers.CharField(error_messages={'required': '必须传入面辅料名称'})
    # m_sample = serializers.CharField(error_messages={'required': '必须传入面辅料规格'})
    # complayer = serializers.CharField(error_messages={'required': '必须传入供应商'})
    # sure_m_sample = serializers.CharField(error_messages={'required': '必须传入面辅料规格确认'})
    # m_unit = serializers.CharField(error_messages={'required': '必须传入用料单位'})
    # m_rate = serializers.CharField(error_messages={'required': '必须传入缩率'})
    # m_use = serializers.CharField(error_messages={'required': '必须传入计划用料'})
    # comments = serializers.CharField(error_messages={'required': '必须传入备注'})
    # price = serializers.CharField(error_messages={'required': '必须传入单价'})
    # total = serializers.CharField(error_messages={'required': '必须传入总金额'})
    id = serializers.IntegerField(default=0)


class planpricesubOneSerializer(serializers.Serializer):
    progrem = serializers.CharField(error_messages={'required': '必须传入成本项目'})
    price = serializers.CharField(error_messages={'required': '必须传入成本项目金额'})
    comments = serializers.CharField(error_messages={'required': '必须传入备注'})
    id = serializers.IntegerField(default=0)


class planpriceOneSerializer(serializers.Serializer):
    good_unit = serializers.CharField(error_messages={'required': '必须传入产品单位'})
    price_type = serializers.CharField(error_messages={'required': '必须传入报价币种'})
    price_rate = serializers.CharField(error_messages={'required': '必须传入报价汇率'})
    gm = serializers.CharField(error_messages={'required': '必须传入毛利率'})
    plan_price = serializers.CharField(error_messages={'required': '必须传入企划报价'})
class planHistoryOneSerializer(serializers.Serializer):
    edition = serializers.IntegerField(error_messages={'required': '必须传入企划版本'})

class planOrderSerializer(serializers.Serializer):
    status = serializers.IntegerField(default=1)
    order_type = serializers.IntegerField(default=0)
    order_custom = serializers.CharField(default="")
    brand = serializers.CharField(default="")
    price_code = serializers.CharField(default="")
    dhkhao = serializers.CharField(default="")
    page_size = serializers.IntegerField(default=10)
    page = serializers.IntegerField(default=1)
    # status = serializers.IntegerField(default=0)
    brand_id = serializers.IntegerField(default=0)
    customer_name_id = serializers.IntegerField(default=0)
    is_pushprogram = serializers.IntegerField(default=999)
    is_workprogram = serializers.IntegerField(default=999)
    is_buyprogram = serializers.IntegerField(default=999)

class planOrderOneSerializer(serializers.Serializer):
    dhkhao = serializers.CharField(error_messages={'required': '必须传入大货款号'})
    department = serializers.CharField(error_messages={'required': '必须传入负责部门'})
    leader = serializers.CharField(error_messages={'required': '必须传入负责人'})
    order_type = serializers.CharField(error_messages={'required': '必须传入订单类型'})
    plan_id = serializers.CharField(error_messages={'required': '必须传入企划id'})
    id = serializers.IntegerField(default=0)

class planOrderLineOneSerializer(serializers.Serializer):
    order_custom = serializers.CharField(error_messages={'required': '必须传入下单客户'})
    custom_type = serializers.CharField(error_messages={'required': '必须传入客户类型'})
    order_type = serializers.CharField(error_messages={'required': '必须传入产品单位'})
    contract_num = serializers.CharField(error_messages={'required': '必须传入合同数量'})
    short_overflow = serializers.CharField(error_messages={'required': '必须传入短溢装'})
    price_terms = serializers.CharField(default="")
    pay_way = serializers.CharField(error_messages={'required': '必须传入付款方式'})
    transportation = serializers.CharField(default='')
    pol = serializers.CharField(default='')
    pod = serializers.CharField(error_messages={'required': '必须传入目的港'})
    exporter_way = serializers.CharField(default='')
    inspect_company = serializers.CharField(error_messages={'required': '必须传入检品公司'})
    delivery_way = serializers.CharField(error_messages={'required': '必须传入提货承运方'})
    send_time = serializers.CharField(error_messages={'required': '必须传入发货时间'})
    inspect_time = serializers.CharField(error_messages={'required': '必须传入质检时间'})
    delivery_time = serializers.CharField(error_messages={'required': '必须传入提货时间'})
    warehouse_time = serializers.CharField(error_messages={'required': '必须传入进仓时间'})
    # order_sn = serializers.CharField(error_messages={'required': '必须传入订单编号'})
    # comments = serializers.CharField(error_messages={'required': '必须传入备注信息'})
    id = serializers.CharField(default=0)

class planOrderGetOneSerializer(serializers.Serializer):
    order_type = serializers.IntegerField(default=0)

class sampleCatalogueOneSerializer(serializers.Serializer):
    samp_name = serializers.CharField(error_messages={'required': '必须传入式样书名称'})
    samp_time = serializers.CharField(error_messages={'required': '必须传入式样书时间'})
    samp_file_url = serializers.CharField(error_messages={'required': '必须传入式样书文件路径'})
    id = serializers.IntegerField(default=0)

class sampleCataGetOneSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(error_messages={'required': '必须传入在建企划ID'})
    id = serializers.IntegerField(default=0)

class plateMakingOneSerializer(serializers.Serializer):
    plate_name = serializers.CharField(error_messages={'required': '必须传入制版名称'})
    plate_time = serializers.CharField(error_messages={'required': '必须传入制版时间'})
    plate_file_url = serializers.CharField(error_messages={'required': '必须传入制版文件路径'})
    id = serializers.IntegerField(default=0)

class plateMakingGetOneSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(error_messages={'required': '必须传入在建企划ID'})
    id = serializers.IntegerField(default=0)

class planColorSpecsSerializer(serializers.Serializer):
    sub_color_id = serializers.IntegerField(error_messages={'required': '必须传入样品子颜色Id'})
    sub_color_name = serializers.CharField(error_messages={'required': '必须传入样品子颜色名称'})
    sub_specs_id = serializers.IntegerField(error_messages={'required': '必须传入样品子规格id'})
    sub_specs_name = serializers.CharField(error_messages={'required': '必须传入样品子规格名称'})
    num = serializers.CharField(error_messages={'required': '必须传入样品数量'})
    id = serializers.IntegerField(default=0)

class planColorSpecsGetOneSerializer(serializers.Serializer):
    pcsl_id = serializers.IntegerField(error_messages={'required': '必须传入成衣样品信息ID'})
    id = serializers.IntegerField(default=0)

class planClothOneSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(error_messages={'required': '必须传入在建企划ID'})
    delivery_mode = serializers.IntegerField(error_messages={'required': '必须传入成衣样品提供方式'})
    department = serializers.CharField(default='')
    member = serializers.CharField(default='')
    custom_type = serializers.CharField(default='')
    custom = serializers.CharField(default='')
    is_fee = serializers.IntegerField(default=0)
    id = serializers.IntegerField(default=0)

class planClothlineSerializer(serializers.Serializer):
    required_time = serializers.CharField(error_messages={'required': '必须传入要求日期'})
    sample_type = serializers.CharField(error_messages={'required': '必须传入成衣样品类型名称'})
    delivery_member = serializers.CharField(error_messages={'required': '必须传入提供人员'})
    send_custom = serializers.CharField(error_messages={'required': '必须传入送达客户'})
    countdown = serializers.CharField(error_messages={'required': '必须传入倒计时'})
    send_num = serializers.IntegerField(default=0)
    send_time = serializers.CharField(error_messages={'required': '必须传入寄送时间'})
    is_fee = serializers.CharField(error_messages={'required': '必须传入是否结算'})
    file_url = serializers.CharField(error_messages={'required': '必须传入资料文件'})
    id = serializers.IntegerField(default=0)

class planClothgetSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(error_messages={'required': '必须传入在建企划ID'})
    delivery_mode = serializers.IntegerField(default=0)
    department = serializers.CharField(default='')
    member = serializers.CharField(default='')
    custom_type = serializers.CharField(default='')
    custom = serializers.CharField(default='')
    is_fee = serializers.IntegerField(default=0)
    id = serializers.IntegerField(default=0)


######################订单管理
class orderOutstockSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})
    order_line_id = serializers.IntegerField(error_messages={'required': '必须传入订单列表id'})
    short_overflow = serializers.IntegerField(error_messages={'required': '必须传入短溢装'})
    short_overflow_direct = serializers.IntegerField(error_messages={'required': '必须传入指示短溢装'})
    dhkhao = serializers.CharField(default='')

class orderOutstockLineSerializer(serializers.Serializer):
    color = serializers.CharField(error_messages={'required': '必须传入面辅料颜色'})
    color_name = serializers.CharField(error_messages={'required': '必须传入服装颜色名称'})
    color_num = serializers.CharField(error_messages={'required': '必须传入客户色号'})
    specs = serializers.CharField(error_messages={'required': '必须传入尺寸'})
    contract_num = serializers.IntegerField(error_messages={'required': '必须传入合同数量'})
    order_num = serializers.IntegerField(error_messages={'required': '必须传入订单数量'})
    id = serializers.IntegerField(default=0)

class orderOutstockGetOneSerializer(serializers.Serializer):
    sort_type = serializers.IntegerField(default=0)

class orderOutstockDeleteOneSerializer(serializers.Serializer):
    order_line_id = serializers.IntegerField(default=0)
    color = serializers.CharField(default="")
    specs = serializers.CharField(default="")


##########出货方案

class machiningSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})
    order_line_id = serializers.IntegerField(error_messages={'required': '必须传入订单列表id'})
    short_overflow = serializers.IntegerField(error_messages={'required': '必须传入短溢装'})
    short_overflow_direct = serializers.IntegerField(error_messages={'required': '必须传入指示短溢装'})
    factory_make_id = serializers.CharField(error_messages={'required': '必须传入加工工厂数据id'})

class machiningLineSerializer(serializers.Serializer):
    color = serializers.CharField(error_messages={'required': '必须传入面辅料颜色'})
    color_name = serializers.CharField(error_messages={'required': '必须传入服装颜色名称'})
    color_num = serializers.CharField(error_messages={'required': '必须传入客户色号'})
    specs = serializers.CharField(error_messages={'required': '必须传入尺寸'})
    contract_num = serializers.IntegerField(error_messages={'required': '必须传入合同数量'})
    order_num = serializers.IntegerField(error_messages={'required': '必须传入订单数量'})
    make_num = serializers.IntegerField(error_messages={'required': '必须传入订单加工数量'})
    id = serializers.IntegerField(default=0)

class machiningGetOneSerializer(serializers.Serializer):
    factory_make_id = serializers.IntegerField(error_messages={'required': '必须传入订单加工工厂方案'})

######################订单管理--工厂方案
class factoryMakeSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})
    work_type = serializers.CharField(error_messages={'required': '必须传入工厂方式'})
    dhkhao = serializers.CharField(default='')

class factoryMakeLineSerializer(serializers.Serializer):
    make_time = serializers.CharField(default='')
    make_factory = serializers.CharField(default='')
    coop_mode = serializers.CharField(default='')
    inspect_company = serializers.CharField(default='')
    order_admin = serializers.CharField(default='')
    ticketing_custom = serializers.CharField(default='')
    id = serializers.IntegerField(default=0)

######################面辅料采购###################################
class orderClothSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})
    plan_id = serializers.IntegerField(error_messages={'required': '必须传入企划id'})
    work_type = serializers.CharField(default='')
    dhkhao = serializers.CharField(default='')

class orderClothLineSerializer(serializers.Serializer):
    plan_material_id = serializers.CharField(error_messages={'required': '必须传入企划用料的id'})
    cloth_type = serializers.CharField(error_messages={'required': '必须传入面辅料类型'})
    cloth_cat = serializers.CharField(error_messages={'required': '必须传入面辅料分类'})
    cloth_name = serializers.CharField(error_messages={'required': '必须传入面辅料名称'})
    delivery_type = serializers.CharField(error_messages={'required': '必须传入收货方式'})
    delivery_name = serializers.CharField(error_messages={'required': '必须传入收货方'})
    is_inspect = serializers.IntegerField(error_messages={'required': '必须传入是否质检'})
    buy_all_num = serializers.IntegerField(error_messages={'required': '必须传入购买数量'})
    loss_lv = serializers.IntegerField(error_messages={'required': '必须传入订单损耗'})
    id = serializers.IntegerField(default=0)

class orderClothLineSubSerializer(serializers.Serializer):
    guige = serializers.CharField(error_messages={'required': '必须传入面辅料规格'})
    buy_num = serializers.CharField(error_messages={'required': '必须传入面辅料采购数量'})
    color = serializers.CharField(default='')
    color_num = serializers.CharField(default='')
    specs = serializers.CharField(default='')
    id = serializers.IntegerField(default=0)

######################发货方案###################################
class orderClothShipSerializer(serializers.Serializer):
    order_cloth_id = serializers.IntegerField(error_messages={'required': '必须传入面辅料采购id'})
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})

class orderClothLineShipSerializer(serializers.Serializer):
    plan_material_id = serializers.CharField(error_messages={'required': '必须传入企划用料的id'})
    cloth_type = serializers.CharField(error_messages={'required': '必须传入面辅料类型'})
    cloth_cat = serializers.CharField(error_messages={'required': '必须传入面辅料分类'})
    cloth_name = serializers.CharField(error_messages={'required': '必须传入面辅料名称'})
    delivery_type = serializers.CharField(error_messages={'required': '必须传入收货方式'})
    delivery_name = serializers.CharField(error_messages={'required': '必须传入收货方'})
    supplier = serializers.CharField(error_messages={'required': '必须传入供应商'})
    all_amount = serializers.IntegerField(error_messages={'required': '必须传入总金额'})
    id = serializers.IntegerField(default=0)

class orderClothLineSubShipSerializer(serializers.Serializer):
    guige = serializers.CharField(error_messages={'required': '必须传入面辅料规格'})
    buy_num = serializers.CharField(error_messages={'required': '必须传入面辅料采购数量'})
    price = serializers.CharField(error_messages={'required': '必须传入面辅料采购单价'})
    amount = serializers.CharField(error_messages={'required': '必须传入面辅料单品总金额'})
    provide_time = serializers.CharField(error_messages={'required': '必须传入交货日期'})
    color = serializers.CharField(default='')
    color_num = serializers.CharField(default='')
    specs = serializers.CharField(default='')
    id = serializers.IntegerField(default=0)

##########面辅料注意事项

class orderNotesSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})
    order_cloth_id = serializers.IntegerField(error_messages={'required': '必须传入面辅料采购id'})

class orderNotesLineSerializer(serializers.Serializer):
    notes_id = serializers.CharField(error_messages={'required': '必须传入注意事项id'})
    beizhu = serializers.CharField(default='')
    people = serializers.CharField(default='')
    people_department = serializers.CharField(default='')
    people_post = serializers.CharField(default='')
    liuyan = serializers.CharField(default='')
    is_sure = serializers.IntegerField(default=0)
    status = serializers.IntegerField(default=0)
    warm_mode_id = serializers.IntegerField(default=0)
    id = serializers.IntegerField(default=0)

class setWarmSerializer(serializers.Serializer):
    warm_type = serializers.IntegerField(error_messages={'required':'必须传入预警类型'})
    warm_time_num = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})
    warm_num_name = serializers.CharField(error_messages={'required': '必须传入预警显示信息！'})
    warm_name = serializers.CharField(error_messages={'required': '必须传入预警类型名称'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class orderNotesOneSerializer(serializers.Serializer):
    order_cloth_id = serializers.IntegerField(error_messages={'required': '必须传入面辅料采购信息id！'})
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id信息！'})

class orderNotesOne1Serializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id信息！'})


class packingSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id信息！'})


class packingLineSerializer(serializers.Serializer):
    order_line_id = serializers.IntegerField(error_messages={'required': '必须传入订单项id'})
    order_type = serializers.IntegerField(error_messages={'required': '必须传入订单类型'})
    order_custom = serializers.CharField(error_messages={'required': '必须传入订单客户'})
    contract_num = serializers.CharField(error_messages={'required': '必须传入合同数量'})
    brand = serializers.CharField(error_messages={'required': '必须传入品牌名称'})
    specs = serializers.CharField(error_messages={'required': '必须传入包装规格'})
    scale = serializers.CharField(error_messages={'required': '必须传入装箱重量标准'})
    cuttle = serializers.CharField(error_messages={'required': '必须传入折叠要求'})
    comments = serializers.CharField(error_messages={'required': '必须传入备注'})
    id = serializers.IntegerField(default=0)


class packingSublineSerializer(serializers.Serializer):
    order_line_id = serializers.IntegerField(error_messages={'required': '必须传入订单项id信息！'})


class packingSubLineoneSerializer(serializers.Serializer):
    out_stock_id = serializers.IntegerField(error_messages={'required': '必须传入工厂方案id'})
    parent_id = serializers.IntegerField(error_messages={'required': '必须传入装箱要求id'})
    pack_num = serializers.IntegerField(error_messages={'required': '必须传入装箱数量'})
    id = serializers.IntegerField(default=0)

######################面辅料确认###################################
class shipmentSureOneSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id信息！'})

class shipmentSureSerializer(serializers.Serializer):
    order_cloth_ship_id = serializers.IntegerField(error_messages={'required': '必须传入面辅料采购id'})
    supplier = serializers.CharField(error_messages={'required': '必须传入面辅料的供应商'})

class shipmentSureLineShipSerializer(serializers.Serializer):
    order_cloth_ship_line_id = serializers.CharField(error_messages={'required': '必须传入面辅料采购列表id'})
    sure_comment = serializers.CharField(error_messages={'required': '必须传入面辅料确认备注'})
    is_sure = serializers.CharField(error_messages={'required': '必须传入面辅料确认操作'})
    sample_send_time = serializers.CharField(error_messages={'required': '必须传入面辅料样料寄送时间'})

class purchasRecordsSerializer(serializers.Serializer):
    send_time = serializers.CharField(error_messages={'required': '必须传入发货日期'})
    up_short_send_num = serializers.IntegerField(error_messages={'required': '必须传入上期欠货数量'})
    send_num = serializers.IntegerField(error_messages={'required': '必须传入本期发货数量'})
    delivery_type = serializers.CharField(error_messages={'required': '必须传入收货方式'})
    delivery_name = serializers.CharField(error_messages={'required': '必须传入收货方'})
    short_send_num = serializers.IntegerField(error_messages={'required': '必须传入本期欠货数量'})
    add_up_num = serializers.IntegerField(error_messages={'required': '必须传入累计发货'})
    take_over_time = serializers.CharField(error_messages={'required': '必须传入收货日期'})
    take_over_num = serializers.IntegerField(error_messages={'required': '必须传入收货数量'})
    id = serializers.IntegerField(default=0)

######################面辅料入库###################################
class shipmentInStockOneSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id信息！'})

class shipmentInStockSerializer(serializers.Serializer):
    order_cloth_ship_id = serializers.IntegerField(error_messages={'required': '必须传入面辅料采购id'})
    supplier = serializers.CharField(error_messages={'required': '必须传入面辅料的供应商'})
    delivery_name = serializers.CharField(error_messages={'required': '必须传入收货方'})

class shipmentInStockLineShipSerializer(serializers.Serializer):
    order_cloth_ship_line_id = serializers.CharField(error_messages={'required': '必须传入面辅料采购列表id'})
    buy_for_num = serializers.CharField(error_messages={'required': '必须传入采购分配数量'})
    short_send_num = serializers.CharField(error_messages={'required': '必须传入欠货数量'})
    add_up_num = serializers.CharField(error_messages={'required': '必须传入累计数量'})

# 短溢装
class shortShipSerializer(serializers.Serializer):
    active = serializers.IntegerField(default=2)
    short_num = serializers.IntegerField(default=0)

class shortShipOneSerializer(serializers.Serializer):
    short_num = serializers.CharField(error_messages={'required':'必须传入短溢装'})
    defalut = serializers.CharField(error_messages={'required': '必须传入默认信息'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class orderDateSetSerializer(serializers.Serializer):
    id = serializers.IntegerField(default=0)

class orderDateSetOneSerializer(serializers.Serializer):
    port_type = serializers.CharField(error_messages={'required':'必须传入出口运输方式'})
    send_num = serializers.CharField(error_messages={'required': '必须传入送检日提前天数'})
    in_num = serializers.CharField(error_messages={'required': '必须传入进仓日天前天数'})
    takeover_num = serializers.CharField(error_messages={'required': '必须传入提货日提前天数'})
    active = serializers.IntegerField(error_messages={'required': '数据参数不可为空！'})

class productReadySerializer(serializers.Serializer):
    factory_make_id = serializers.IntegerField(error_messages={'required': '必须传入加工工厂id'})
    # order_id = serializers.CharField(error_messages={'required': '必须传入订单的id'})
    plan_start_date = serializers.CharField(error_messages={'required': '必须传入计划上手日期'})


class productReadyoneSerializer(serializers.Serializer):
    brand = serializers.CharField(default="")
    price_code = serializers.CharField(default="")
    dhkhao = serializers.CharField(default="")
    page_size = serializers.IntegerField(default=10)
    page = serializers.IntegerField(default=1)
    make_factory = serializers.CharField(default="")

class subMissionSerializer(serializers.Serializer):
    kuan_hao = serializers.CharField(error_messages={'required': '必须传入款号'})
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单的id'})
    custom = serializers.CharField(error_messages={'required': '必须传入客户'})
    order_line_id = serializers.IntegerField(error_messages={'required': '必须传入订单项id'})
    submis_people = serializers.CharField(error_messages={'required': '必须传入负责人'})
    start_num = serializers.CharField(error_messages={'required': '必须传入箱号（前）'})
    end_num = serializers.CharField(error_messages={'required': '必须传入箱号（后）'})
    box_num = serializers.IntegerField(error_messages={'required': '必须传入箱数'})
    color = serializers.CharField(error_messages={'required': '必须传入颜色'})
    size1 = serializers.CharField(error_messages={'required': '必须传入尺码X'})
    size2 = serializers.CharField(error_messages={'required': '必须传入尺码F'})
    size3 = serializers.CharField(error_messages={'required': '必须传入尺码Z'})
    number = serializers.IntegerField(error_messages={'required': '必须传入数量'})
    total = serializers.IntegerField(error_messages={'required': '必须传入小结'})
    gross_weight = serializers.IntegerField(error_messages={'required': '必须传入毛重量'})
    net_weight = serializers.IntegerField(error_messages={'required': '必须传入净重量'})
    volume = serializers.CharField(error_messages={'required': '必须传入体积'})
    id = serializers.IntegerField(default=0)

class submisInfoSerializer(serializers.Serializer):
    info = serializers.CharField(error_messages={'required': '必须传入附件路径'})
    order_line_id = serializers.IntegerField(error_messages={'required': '必须传入订单项的id'})
    factory_name = serializers.CharField(error_messages={'required': '必须传入工厂名称'})


class indicateDateoneSerializer(serializers.Serializer):
    indicate_time = serializers.CharField(error_messages={'required': '必须传入指示发货日期！'})
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})
    order_line_id = serializers.IntegerField(error_messages={'required': '必须传入订单项id'})
    delivery_way = serializers.CharField(error_messages={'required': '必须传入提货承运人'})
    transportation = serializers.CharField(error_messages={'required': '必须传入出口运输方式'})
    exporter_way = serializers.CharField(error_messages={'required': '必须传入出口承运方'})

class indicateDateSerializer(serializers.Serializer):
    order_custom = serializers.CharField(default="")
    price_code = serializers.CharField(default="")
    dhkhao = serializers.CharField(default="")
    page_size = serializers.IntegerField(default=10)
    page = serializers.IntegerField(default=1)
    order_type = serializers.IntegerField(default=0)

class colorSizeDataSerializer(serializers.Serializer):
    order_color_size_info = serializers.CharField(error_messages={'required': '必须传入订单颜色规格信息！'})
    order_id = serializers.IntegerField(error_messages={'required': '必须传入订单id'})

class reightSpaceSerializer(serializers.Serializer):
    indicate_time = serializers.CharField(error_messages={'required': '必须传入指示发货日期！'})
    order_line_ids = serializers.CharField(error_messages={'required': '必须传入订单项id'})
    shou_huo_term_name = serializers.CharField(default="")
    shou_huo_term_id = serializers.IntegerField(default=0)
    space_name = serializers.CharField(default="")
    pol = serializers.CharField(error_messages={'required': '必须传入起运港'})
    pod = serializers.CharField(error_messages={'required': '必须传入目的港'})
    transportation = serializers.CharField(error_messages={'required': '必须传入出口运输方式'})
    exporter_way = serializers.CharField(error_messages={'required': '必须传入出口承运方'})
    id = serializers.IntegerField(default=0)

class reightSpaceLineSerializer(serializers.Serializer):
    order_type = serializers.IntegerField(default=0)
    order_custom = serializers.CharField(default="")
    price_code = serializers.CharField(default="")
    dhkhao = serializers.CharField(default="")
    page_size = serializers.IntegerField(default=10)
    page = serializers.IntegerField(default=1)

class reightSpaceOneSerializer(serializers.Serializer):
    info_url = serializers.CharField(error_messages={'required': '必须传入确认仓位信息'})
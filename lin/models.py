# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Archives(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    job_number = models.IntegerField()
    name = models.CharField(max_length=20)
    gender = models.SmallIntegerField()
    birthday = models.DateField(blank=True, null=True)
    department_id = models.IntegerField()
    post_id = models.IntegerField()
    phone = models.CharField(max_length=11)
    emergency_contact = models.CharField(max_length=20)
    emergency_phone = models.CharField(max_length=11)
    due_to_time = models.DateField()
    status = models.SmallIntegerField(blank=True, null=True)
    enter_time = models.DateTimeField(blank=True, null=True)
    leave_time = models.DateTimeField(blank=True, null=True)
    birthday_mouth = models.SmallIntegerField(blank=True, null=True)
    birthday_day = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archives'


class ArchivesSalaryDetail(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    archives_id = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    mouth = models.IntegerField(blank=True, null=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    social_insurance_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_contributions_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    calculated_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    real_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archives_salary_detail'


class ArchivesSalaryInfo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    archives_id = models.IntegerField(blank=True, null=True)
    social_insurance_level = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    annual_salary = models.IntegerField(blank=True, null=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    social_insurance_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    social_insurance_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_contributions_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_contributions_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_level = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    calculated_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    real_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deducton_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archives_salary_info'


class ArchivesSalaryStandard(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    archives_id = models.IntegerField(blank=True, null=True)
    social_insurance_id = models.IntegerField(blank=True, null=True)
    social_insurance_level = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    annual_salary = models.IntegerField(blank=True, null=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    social_insurance_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    social_insurance_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_contributions_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_contributions_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_id = models.IntegerField(blank=True, null=True)
    surplu_level = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archives_salary_standard'


class Authority(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    authority_name = models.CharField(max_length=25)
    role_id = models.IntegerField()
    select_status = models.IntegerField()
    modify_status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'authority'


class AuthorityInfo(models.Model):
    authority_name = models.CharField(max_length=255, blank=True, null=True)
    authority_sn = models.CharField(max_length=255, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    father_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'authority_info'


class BaseWarm(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    warm_type = models.IntegerField(blank=True, null=True)
    warm_time_num = models.IntegerField(blank=True, null=True)
    warm_num_name = models.CharField(max_length=255, blank=True, null=True)
    warm_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'base_warm'


class Basic(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    basic_value_zh = models.CharField(max_length=100)
    basic_value_en = models.CharField(max_length=100)
    type_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'basic'


class BasicType(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'basic_type'


class Book(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=30, blank=True, null=True)
    summary = models.CharField(max_length=1000, blank=True, null=True)
    image = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book'


class Client(models.Model):
    name = models.CharField(max_length=30)
    shop_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    party = models.IntegerField()
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'client'


class Cloth(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    cloth = models.CharField(max_length=100)
    class_id = models.IntegerField()
    weight = models.IntegerField(blank=True, null=True)
    active = models.SmallIntegerField()
    checked = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'cloth'


class ClothCategory(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    cloth_id = models.IntegerField()
    category_name = models.CharField(max_length=100)
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cloth_category'


class ClothClass(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    cloth_class_name = models.CharField(max_length=25)
    weight = models.IntegerField(blank=True, null=True)
    active = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'cloth_class'


class ClothColour(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    colour_name = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cloth_colour'


class ClothMaterial(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    material = models.CharField(max_length=100)
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)
    cloth_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cloth_material'


class ClothNotes(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    category_id = models.IntegerField()
    notes_name = models.CharField(max_length=100)
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cloth_notes'


class ClothSpecs(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    specs_name = models.CharField(max_length=25)
    specs_unit = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cloth_specs'


class CompanyInfo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    company_name = models.CharField(max_length=20)
    credit_code = models.CharField(max_length=20)
    company_address = models.CharField(max_length=100)
    phone = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=20)
    bank_account = models.CharField(max_length=20)
    customer_file_id = models.IntegerField()
    resource_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'company_info'


class CompanyPlan(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    brand_id = models.IntegerField()
    customer_name_id = models.IntegerField()
    plan_id = models.IntegerField()
    plan_org_id = models.IntegerField()
    material_plan_id = models.IntegerField()
    price_id = models.IntegerField()
    goods_name = models.CharField(max_length=255, blank=True, null=True)
    price_code = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'company_plan'


class Contracts(models.Model):
    items = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    merchant_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contracts'


class CustomerCompany(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    language = models.CharField(max_length=10)
    company_name = models.CharField(max_length=100)
    company_name_simple = models.CharField(max_length=100)
    country = models.CharField(max_length=20)
    company_address = models.CharField(max_length=200)
    customer_file_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'customer_company'


class CustomerContact(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    customer_id = models.IntegerField()
    department_name = models.CharField(max_length=25, blank=True, null=True)
    post_name = models.CharField(max_length=25, blank=True, null=True)
    contact_name = models.CharField(max_length=25, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    email = models.CharField(max_length=25, blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer_contact'


class CustomerFiles(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    type_id = models.IntegerField()
    customer_full_name = models.CharField(max_length=250, blank=True, null=True)
    customer_simple_name = models.CharField(max_length=250, blank=True, null=True)
    office_phone = models.CharField(max_length=25, blank=True, null=True)
    fax_number = models.CharField(max_length=25, blank=True, null=True)
    active = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'customer_files'


class CustomerType(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    customer_type = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()
    selected_single = models.SmallIntegerField()
    selected_invoice = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'customer_type'


class DataTemplate(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    type_id = models.SmallIntegerField()
    name = models.CharField(max_length=100)
    template_url = models.CharField(max_length=255)
    required = models.SmallIntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'data_template'


class DataTemplateArchives(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    type_id = models.SmallIntegerField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    template_url = models.CharField(max_length=255, blank=True, null=True)
    required = models.SmallIntegerField(blank=True, null=True)
    active = models.SmallIntegerField(blank=True, null=True)
    archives_id = models.IntegerField(blank=True, null=True)
    template_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_template_archives'


class Department(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    department_name = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'department'


class FMakeBNumData(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    out_stock_id = models.IntegerField(blank=True, null=True)
    b_num = models.IntegerField(blank=True, null=True)
    make_num = models.IntegerField(blank=True, null=True)
    factory_make_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'f_make_b_num_data'


class FactoryMake(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_num_all = models.IntegerField(blank=True, null=True)
    make_num = models.IntegerField(blank=True, null=True)
    make_time = models.DateTimeField(blank=True, null=True)
    make_factory = models.CharField(max_length=255, blank=True, null=True)
    coop_mode = models.CharField(max_length=255, blank=True, null=True)
    inspect_company = models.CharField(max_length=255, blank=True, null=True)
    order_admin = models.CharField(max_length=255, blank=True, null=True)
    ticketing_custom = models.CharField(max_length=255, blank=True, null=True)
    plan_start_date = models.DateTimeField(blank=True, null=True)
    real_start_date = models.DateTimeField(blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    inspect_name = models.CharField(max_length=255, blank=True, null=True)
    inspect_url = models.TextField(blank=True, null=True)
    is_b_sure = models.IntegerField(db_column='is_B_sure', blank=True, null=True)  # Field name made lowercase.
    make_pay_num = models.IntegerField(blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sure_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure_pay = models.IntegerField(blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    finish_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sample_sure_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure_pay_sample = models.IntegerField(blank=True, null=True)
    finish_sample_amount = models.CharField(max_length=255, blank=True, null=True)
    b_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'factory_make'


class FactoryMakeLine(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    color_name = models.CharField(max_length=255, blank=True, null=True)
    color_num = models.CharField(max_length=255, blank=True, null=True)
    specs = models.CharField(max_length=255, blank=True, null=True)
    contract_num = models.IntegerField(blank=True, null=True)
    short_overflow = models.IntegerField(blank=True, null=True)
    short_overflow_direct = models.IntegerField(blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    make_num = models.IntegerField(blank=True, null=True)
    no_allocation_num = models.IntegerField(blank=True, null=True)
    factory_make_id = models.IntegerField(blank=True, null=True)
    b_num = models.IntegerField(blank=True, null=True)
    is_b_sure = models.IntegerField(db_column='is_B_sure', blank=True, null=True)  # Field name made lowercase.
    inspect_num = models.IntegerField(blank=True, null=True)
    recover_b_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'factory_make_line'


class FeeNo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=255, blank=True, null=True)
    amount = models.CharField(max_length=255, blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    make_factory_id = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    order_cloth_ship_id = models.IntegerField(blank=True, null=True)
    other_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fee_no'


class FinanceCatSon(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    finance_son_name = models.CharField(max_length=100)
    f_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_cat_son'


class FinanceCatSub(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    finance_sub_name = models.CharField(max_length=100)
    f_id = models.IntegerField()
    s_id = models.IntegerField(blank=True, null=True)
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_cat_sub'


class FinanceMouthInfo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    finance_sub_id = models.IntegerField(blank=True, null=True)
    finance_son_id = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    post = models.CharField(max_length=255, blank=True, null=True)
    worker = models.CharField(max_length=255, blank=True, null=True)
    learder = models.CharField(max_length=255, blank=True, null=True)
    fee_info_name = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=255, blank=True, null=True)
    mouth = models.CharField(max_length=255, blank=True, null=True)
    amount_type = models.IntegerField(blank=True, null=True)
    amount_type_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_mouth_info'


class GarmentSampleRecord(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    plan_id = models.SmallIntegerField()
    sample_method = models.IntegerField()
    customer_type_id = models.IntegerField()
    customer_name_id = models.IntegerField()
    required_date = models.DateField()
    sample_type_name_id = models.IntegerField()
    provide_personnel_id = models.IntegerField()
    delivery_customer_id = models.IntegerField()
    delivery_time = models.CharField(max_length=25)
    balance = models.SmallIntegerField()
    payment_fee = models.SmallIntegerField()
    resource_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'garment_sample_record'


class GoodsSize(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    goods_size = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'goods_size'


class Harbour(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    harbour_zh = models.CharField(max_length=25)
    harbour_en = models.CharField(max_length=25)
    harbour_type = models.IntegerField()
    order_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'harbour'


class Image(models.Model):
    url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'image'


class IndicateTime(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    indicate_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'indicate_time'


class InvoiceSetting(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    prefix_type = models.SmallIntegerField()
    prefix_name = models.CharField(max_length=25)
    code_number_start = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'invoice_setting'


class JobNumber(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    sort_type = models.SmallIntegerField()
    start_number = models.CharField(max_length=25, blank=True, null=True)
    end_number = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_number'


class MakeFatoryInspect(models.Model):
    dhkh = models.CharField(max_length=255, blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    make_factory_id = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    box_hao_start = models.IntegerField(blank=True, null=True)
    box_hao_end = models.IntegerField(blank=True, null=True)
    box_hao_type = models.CharField(max_length=255, blank=True, null=True)
    box_num = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    specs = models.TextField(blank=True, null=True)
    num = models.IntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    gw = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nw = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    meas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    make_factory = models.CharField(max_length=255, blank=True, null=True)
    inspect_num = models.IntegerField(blank=True, null=True)
    b_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'make_fatory_inspect'


class Marks(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    brand = models.CharField(max_length=20)
    brand_url = models.CharField(max_length=200)
    active = models.SmallIntegerField()
    namecard_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'marks'


class OrderCloth(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    cloth_type = models.IntegerField(blank=True, null=True)
    cloth_cat = models.CharField(max_length=255, blank=True, null=True)
    cloth_name = models.CharField(max_length=255, blank=True, null=True)
    delivery_type = models.CharField(max_length=255, blank=True, null=True)
    delivery_name = models.CharField(max_length=255, blank=True, null=True)
    is_inspect = models.IntegerField(blank=True, null=True)
    buy_all_num = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    loss_lv = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    plan_material_id = models.IntegerField(blank=True, null=True)
    is_sure_in_store = models.IntegerField(blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_new = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_cloth'


class OrderClothLine(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_cloth_id = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    color_name = models.CharField(max_length=255, blank=True, null=True)
    color_num = models.CharField(max_length=255, blank=True, null=True)
    guige = models.CharField(max_length=255, blank=True, null=True)
    specs = models.CharField(max_length=255, blank=True, null=True)
    contract_num = models.IntegerField(blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    suo_lv = models.IntegerField(blank=True, null=True)
    buy_num = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_inspect = models.IntegerField(blank=True, null=True)
    inspect_content = models.CharField(max_length=255, blank=True, null=True)
    drop_status = models.IntegerField(blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_sure_in_store = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_cloth_line'


class OrderClothLineShip(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_cloth_id = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    color_name = models.CharField(max_length=255, blank=True, null=True)
    color_num = models.CharField(max_length=255, blank=True, null=True)
    guige = models.CharField(max_length=255, blank=True, null=True)
    specs = models.CharField(max_length=255, blank=True, null=True)
    delivery_name = models.CharField(max_length=255, blank=True, null=True)
    delivery_type = models.CharField(max_length=255, blank=True, null=True)
    contract_num = models.IntegerField(blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    suo_lv = models.IntegerField(blank=True, null=True)
    provide_num = models.IntegerField(blank=True, null=True)
    buy_num = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_cloth_line_id = models.IntegerField(blank=True, null=True)
    order_cloth_ship_id = models.IntegerField(blank=True, null=True)
    provide_time = models.DateTimeField(blank=True, null=True)
    sample_send_time = models.DateTimeField(blank=True, null=True)
    sure_comment = models.CharField(max_length=255, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    buy_for_num = models.IntegerField(blank=True, null=True)
    short_send_num = models.IntegerField(blank=True, null=True)
    add_up_num = models.IntegerField(blank=True, null=True)
    is_sure_in_store = models.IntegerField(blank=True, null=True)
    is_sure_pay = models.IntegerField(blank=True, null=True)
    sure_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_cloth_line_ship'


class OrderClothShip(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    cloth_type = models.IntegerField(blank=True, null=True)
    cloth_cat = models.CharField(max_length=255, blank=True, null=True)
    cloth_name = models.CharField(max_length=255, blank=True, null=True)
    delivery_type = models.CharField(max_length=255, blank=True, null=True)
    delivery_name = models.CharField(max_length=255, blank=True, null=True)
    is_inspect = models.IntegerField(blank=True, null=True)
    buy_all_num = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    loss_lv = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    all_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_cloth_id = models.IntegerField(blank=True, null=True)
    plan_material_id = models.IntegerField(blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_sure_in_store = models.IntegerField(blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    is_sure_pay = models.IntegerField(blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    is_new = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_cloth_ship'


class OrderColorSizeInfo(models.Model):
    order_id = models.IntegerField(blank=True, null=True)
    order_color_size_info = models.TextField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    packing_info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_color_size_info'


class OrderDateSet(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    takeover_num = models.IntegerField(blank=True, null=True)
    in_num = models.IntegerField(blank=True, null=True)
    send_num = models.IntegerField(blank=True, null=True)
    port_type = models.CharField(max_length=255, blank=True, null=True)
    defalut = models.SmallIntegerField(blank=True, null=True)
    active = models.SmallIntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_date_set'


class OrderLinePacking(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_custom = models.CharField(max_length=255, blank=True, null=True)
    order_type = models.CharField(max_length=255, blank=True, null=True)
    contract_num = models.IntegerField(blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    specs = models.CharField(max_length=255, blank=True, null=True)
    scale = models.CharField(max_length=255, blank=True, null=True)
    cuttle = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_line_packing'


class OrderLinePackingSub(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    pack_num = models.IntegerField(blank=True, null=True)
    out_stock_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_line_packing_sub'


class OrderNotes(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    notes_id = models.IntegerField(blank=True, null=True)
    beizhu = models.CharField(max_length=255, blank=True, null=True)
    warm_time = models.DateTimeField(blank=True, null=True)
    people = models.CharField(max_length=255, blank=True, null=True)
    people_department = models.CharField(max_length=255, blank=True, null=True)
    people_post = models.CharField(max_length=255, blank=True, null=True)
    liuyan = models.CharField(max_length=255, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    warm_mode_id = models.CharField(max_length=255, blank=True, null=True)
    warm_day_num = models.IntegerField(blank=True, null=True)
    warm_status_day_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_notes'


class OrderNotesOther(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    notes_id = models.IntegerField(blank=True, null=True)
    beizhu = models.CharField(max_length=255, blank=True, null=True)
    warm_time = models.DateTimeField(blank=True, null=True)
    people = models.CharField(max_length=255, blank=True, null=True)
    people_department = models.CharField(max_length=255, blank=True, null=True)
    people_post = models.CharField(max_length=255, blank=True, null=True)
    liuyan = models.CharField(max_length=255, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    warm_mode_id = models.CharField(max_length=255, blank=True, null=True)
    warm_day_num = models.IntegerField(blank=True, null=True)
    warm_status_day_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_notes_other'


class OrderPackInfo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    extent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    box_num = models.IntegerField(blank=True, null=True)
    box_pack_num = models.IntegerField(blank=True, null=True)
    predict_volume = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    pack_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    box_rough_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_net_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_rough_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_pack_info'


class OrderPay(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    pay_content = models.CharField(max_length=255, blank=True, null=True)
    pay_type = models.CharField(max_length=255, blank=True, null=True)
    pay_num = models.IntegerField(blank=True, null=True)
    pay_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure_price = models.IntegerField(blank=True, null=True)
    pay_y_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_n_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=255, blank=True, null=True)
    fee_amount = models.CharField(max_length=255, blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    fee_no_status = models.CharField(max_length=255, blank=True, null=True)
    provide_custom = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_pay'


class OrderPayInfoList(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    pay_time = models.DateTimeField(blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    custom_type = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    pay_mode = models.CharField(max_length=255, blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_y_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_n_amount_one = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    beizhun = models.CharField(max_length=255, blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    order_other_pay_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_pay_info_list'


class OrderSurBp(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.CharField(max_length=255, blank=True, null=True)
    sur_lv = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sur_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sur_bp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bp_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_pay = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_sur_bp'


class OtherAccountNew(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    pay_custom = models.CharField(max_length=255, blank=True, null=True)
    pay_comment = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    pay_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_num = models.IntegerField(blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    finish_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=255, blank=True, null=True)
    fee_amount = models.CharField(max_length=255, blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    fee_no_status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_account_new'


class OtherCategory(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    category_name = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()
    category_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_category'


class OtherCategorySetting(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    sub_category_id = models.IntegerField()
    category_set_name = models.CharField(max_length=100)
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_category_setting'


class OtherNotes(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    category_setting_id = models.IntegerField()
    notes_name = models.CharField(max_length=100)
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_notes'


class OtherSubCategory(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    sub_name = models.CharField(max_length=25)
    category_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'other_sub_category'


class OutStock(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    color_name = models.CharField(max_length=255, blank=True, null=True)
    color_num = models.CharField(max_length=255, blank=True, null=True)
    specs = models.CharField(max_length=255, blank=True, null=True)
    contract_num = models.IntegerField(blank=True, null=True)
    short_overflow = models.IntegerField(blank=True, null=True)
    short_overflow_direct = models.IntegerField(blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    b_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'out_stock'


class OutStockSureimg(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_cloth_ship_id = models.IntegerField(blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    pic_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'out_stock__sureimg'


class Plan(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    brand_id = models.IntegerField()
    customer_name_id = models.IntegerField()
    plan_department = models.CharField(max_length=255, blank=True, null=True)
    plan_post = models.CharField(max_length=255, blank=True, null=True)
    plan_id = models.IntegerField()
    plan_org_department = models.CharField(max_length=255, blank=True, null=True)
    plan_org_post = models.CharField(max_length=255, blank=True, null=True)
    plan_org_id = models.IntegerField()
    material_plan_department = models.CharField(max_length=255, blank=True, null=True)
    material_plan_post = models.CharField(max_length=255, blank=True, null=True)
    material_plan_id = models.IntegerField()
    price_post = models.CharField(max_length=255, blank=True, null=True)
    price_department = models.CharField(max_length=255, blank=True, null=True)
    price_id = models.IntegerField()
    goods_name = models.CharField(max_length=255, blank=True, null=True)
    price_code = models.CharField(max_length=255)
    status = models.IntegerField(blank=True, null=True)
    plan_datetime = models.DateTimeField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan'


class PlanClothSample(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    delivery_mode = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    member = models.CharField(max_length=255, blank=True, null=True)
    custom_type = models.CharField(max_length=255, blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    is_fee = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_cloth_sample'


class PlanClothSampleLine(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    pcs_id = models.IntegerField(blank=True, null=True)
    required_time = models.DateTimeField(blank=True, null=True)
    sample_type = models.CharField(max_length=255, blank=True, null=True)
    delivery_member = models.CharField(max_length=255, blank=True, null=True)
    send_custom = models.CharField(max_length=255, blank=True, null=True)
    countdown = models.CharField(max_length=255, blank=True, null=True)
    send_num = models.IntegerField(blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    is_pay = models.IntegerField(blank=True, null=True)
    is_fee = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    delivery_mode = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    member = models.CharField(max_length=255, blank=True, null=True)
    custom_type = models.CharField(max_length=255, blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_export = models.IntegerField(blank=True, null=True)
    pay_custom = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_cloth_sample_line'


class PlanClothSampleNumber(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    pcsl_id = models.IntegerField(blank=True, null=True)
    sub_color_id = models.IntegerField(blank=True, null=True)
    sub_color_name = models.CharField(max_length=255, blank=True, null=True)
    sub_specs_id = models.IntegerField(blank=True, null=True)
    sub_specs_name = models.CharField(max_length=255, blank=True, null=True)
    num = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_cloth_sample_number'


class PlanMaterial(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    m_cat = models.CharField(max_length=255, blank=True, null=True)
    m_name = models.CharField(max_length=255, blank=True, null=True)
    m_sample = models.CharField(max_length=255, blank=True, null=True)
    complayer = models.CharField(max_length=255, blank=True, null=True)
    sure_m_sample = models.CharField(max_length=255, blank=True, null=True)
    m_unit = models.CharField(max_length=255, blank=True, null=True)
    m_rate = models.CharField(max_length=255, blank=True, null=True)
    m_use = models.IntegerField(blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    is_finish = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_material'


class PlanMaterialCopy(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    m_cat = models.CharField(max_length=255, blank=True, null=True)
    m_name = models.CharField(max_length=255, blank=True, null=True)
    m_sample = models.CharField(max_length=255, blank=True, null=True)
    complayer = models.CharField(max_length=255, blank=True, null=True)
    sure_m_sample = models.CharField(max_length=255, blank=True, null=True)
    m_unit = models.CharField(max_length=255, blank=True, null=True)
    m_rate = models.IntegerField(blank=True, null=True)
    m_use = models.IntegerField(blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    old_id = models.IntegerField(blank=True, null=True)
    is_finish = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_material_copy'


class PlanOrder(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    dhkhao = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    leader = models.CharField(max_length=255, blank=True, null=True)
    lead_id = models.IntegerField(blank=True, null=True)
    order_type = models.CharField(max_length=255, blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    price_code = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    goods_name = models.CharField(max_length=255, blank=True, null=True)
    plan_time = models.DateTimeField(blank=True, null=True)
    plan_status = models.CharField(max_length=255, blank=True, null=True)
    workflow = models.CharField(max_length=255, blank=True, null=True)
    contract_num = models.IntegerField(blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    is_pushprogram = models.IntegerField(blank=True, null=True)
    is_workprogram = models.IntegerField(blank=True, null=True)
    is_buyprogram = models.IntegerField(blank=True, null=True)
    pushprogram_num = models.IntegerField(blank=True, null=True)
    workprogram_num = models.IntegerField(blank=True, null=True)
    buyprogram_num = models.IntegerField(blank=True, null=True)
    order_line_num = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    work_type = models.CharField(max_length=255, blank=True, null=True)
    plan_start_date = models.DateTimeField(blank=True, null=True)
    real_start_date = models.DateTimeField(blank=True, null=True)
    is_sure_drop_lable = models.IntegerField(blank=True, null=True)
    inspect_name = models.CharField(max_length=255, blank=True, null=True)
    indicate_flag = models.CharField(max_length=255, blank=True, null=True)
    indicate_time = models.DateField(blank=True, null=True)
    export_goods_name = models.CharField(max_length=255, blank=True, null=True)
    inport_goods_name = models.CharField(max_length=255, blank=True, null=True)
    inspect_send_info_person = models.CharField(max_length=255, blank=True, null=True)
    pay_status = models.IntegerField(blank=True, null=True)
    invoice_num = models.CharField(max_length=255, blank=True, null=True)
    fee_num = models.CharField(max_length=255, blank=True, null=True)
    sure_status = models.IntegerField(blank=True, null=True)
    provide_custom = models.CharField(max_length=255, blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    is_surrender = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_order'


class PlanOrderLine(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    custom_type = models.CharField(max_length=255, blank=True, null=True)
    order_custom = models.CharField(max_length=255, blank=True, null=True)
    order_type = models.IntegerField(blank=True, null=True)
    contract_num = models.IntegerField(blank=True, null=True)
    short_overflow = models.IntegerField(blank=True, null=True)
    short_overflow_direct = models.IntegerField(blank=True, null=True)
    price_terms = models.CharField(max_length=255, blank=True, null=True)
    pay_way = models.CharField(max_length=255, blank=True, null=True)
    transportation = models.CharField(max_length=255, blank=True, null=True)
    pol = models.CharField(max_length=255, blank=True, null=True)
    pod = models.CharField(max_length=255, blank=True, null=True)
    exporter_way = models.CharField(max_length=255, blank=True, null=True)
    inspect_company = models.CharField(max_length=255, blank=True, null=True)
    delivery_way = models.CharField(max_length=255, blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    inspect_time = models.DateTimeField(blank=True, null=True)
    delivery_time = models.DateTimeField(blank=True, null=True)
    warehouse_time = models.DateTimeField(blank=True, null=True)
    order_sn = models.CharField(max_length=255, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    is_work_progrem = models.IntegerField(blank=True, null=True)
    is_pushprogram = models.IntegerField(blank=True, null=True)
    is_buyprogram = models.IntegerField(blank=True, null=True)
    order_num = models.IntegerField(blank=True, null=True)
    indicate_time = models.DateTimeField(blank=True, null=True)
    reight_space_id = models.IntegerField(blank=True, null=True)
    drop_url = models.CharField(max_length=255, blank=True, null=True)
    lable_url = models.CharField(max_length=255, blank=True, null=True)
    is_shipping = models.IntegerField(blank=True, null=True)
    order_price_type = models.CharField(max_length=255, blank=True, null=True)
    order_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure_price = models.IntegerField(blank=True, null=True)
    pay_y_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_n_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    provide_custom = models.CharField(max_length=255, blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=255, blank=True, null=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fee_no_status = models.IntegerField(blank=True, null=True)
    reightspace_flag = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_order_line'


class PlanPrice(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    good_unit = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    price_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    is_finish = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_price'


class PlanPriceCopy(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    good_unit = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    price_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    old_id = models.IntegerField(blank=True, null=True)
    is_finish = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_price_copy'


class PlanPriceSub(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    plan_price_id = models.IntegerField(blank=True, null=True)
    progrem = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    is_finish = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_price_sub'


class PlanPriceSubCopy(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    plan_price_id = models.IntegerField(blank=True, null=True)
    progrem = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    old_id = models.IntegerField(blank=True, null=True)
    is_finish = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_price_sub_copy'


class PlateMaking(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    plate_name = models.CharField(max_length=255, blank=True, null=True)
    plate_time = models.DateTimeField(blank=True, null=True)
    plate_file_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plate_making'


class Post(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    post_name = models.CharField(max_length=25)
    department_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'post'


class ProductPayInfo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    product_pay_static_id = models.IntegerField(blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    pay_mode = models.CharField(max_length=255, blank=True, null=True)
    pay_now_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_all_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_no_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_entrust = models.IntegerField(blank=True, null=True)
    entrust_company = models.CharField(max_length=255, blank=True, null=True)
    entrust_book = models.CharField(max_length=255, blank=True, null=True)
    beizhu = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_pay_info'


class ProductPayStatic(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    pay_project = models.CharField(max_length=255, blank=True, null=True)
    custom_type = models.CharField(max_length=255, blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    pay_custom = models.CharField(max_length=255, blank=True, null=True)
    pay_comment = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    pay_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_num = models.IntegerField(blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    finish_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    factory_make_id = models.IntegerField(blank=True, null=True)
    order_cloth_ship_id = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=255, blank=True, null=True)
    fee_amount = models.CharField(max_length=255, blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    fee_no_status = models.CharField(max_length=255, blank=True, null=True)
    set_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_pay_static'


class PurchasingRecords(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    up_short_send_num = models.IntegerField(blank=True, null=True)
    send_num = models.IntegerField(blank=True, null=True)
    delivery_type = models.CharField(max_length=255, blank=True, null=True)
    delivery_name = models.CharField(max_length=255, blank=True, null=True)
    short_send_num = models.IntegerField(blank=True, null=True)
    add_up_num = models.IntegerField(blank=True, null=True)
    take_over_time = models.DateTimeField(blank=True, null=True)
    take_over_num = models.IntegerField(blank=True, null=True)
    order_cloth_line_ship_id = models.IntegerField(blank=True, null=True)
    take_over_url = models.TextField(blank=True, null=True)
    send_over_url = models.TextField(blank=True, null=True)
    take_over_url_num = models.IntegerField(blank=True, null=True)
    send_over_url_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purchasing_records'


class ReceivingGoodsMethod(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    method_name = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'receiving_goods_method'


class ReightSpace(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    exporter_way = models.CharField(max_length=255, blank=True, null=True)
    shou_huo_term_name = models.CharField(max_length=255, blank=True, null=True)
    shou_huo_term_id = models.IntegerField(blank=True, null=True)
    space_name = models.CharField(max_length=255, blank=True, null=True)
    reight_s_time = models.DateTimeField(blank=True, null=True)
    info_url = models.CharField(max_length=255, blank=True, null=True)
    pol = models.CharField(max_length=255, blank=True, null=True)
    pod = models.CharField(max_length=255, blank=True, null=True)
    transportation = models.CharField(max_length=255, blank=True, null=True)
    order_line_ids = models.CharField(max_length=255, blank=True, null=True)
    indicate_time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    reightspace_flag = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reight_space'


class Role(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    role_name = models.CharField(max_length=25)
    active = models.SmallIntegerField()
    weight = models.IntegerField()
    authority_list = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role'


class RoleMenu(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    archives_id = models.IntegerField()
    name = models.CharField(max_length=255)
    role_id = models.IntegerField(blank=True, null=True)
    active = models.SmallIntegerField()
    password = models.CharField(max_length=255, blank=True, null=True)
    pc_client = models.SmallIntegerField(blank=True, null=True)
    app_client = models.SmallIntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role_menu'


class SampPayFeeInfo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    udate_time = models.DateTimeField(blank=True, null=True)
    deletw_time = models.DateTimeField(blank=True, null=True)
    factory_make_id = models.IntegerField(blank=True, null=True)
    samp_id = models.CharField(max_length=255, blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_finish = models.IntegerField(blank=True, null=True)
    finish_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fee_no = models.CharField(max_length=255, blank=True, null=True)
    fee_amount = models.CharField(max_length=255, blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    fee_no_status = models.CharField(max_length=255, blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    pay_comment = models.CharField(max_length=255, blank=True, null=True)
    pay_custom = models.CharField(max_length=255, blank=True, null=True)
    pay_project = models.CharField(max_length=255, blank=True, null=True)
    pay_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'samp_pay_fee_info'


class SampTools(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    tools_name = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    fee_lv_1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fee_lv_2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'samp_tools'


class SampleCatalogue(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    plan_id = models.IntegerField(blank=True, null=True)
    samp_name = models.CharField(max_length=255, blank=True, null=True)
    samp_time = models.DateTimeField(blank=True, null=True)
    samp_file_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sample_catalogue'


class SamplePayInfoList(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    pay_time = models.DateTimeField(blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    custom_type = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    pay_mode = models.CharField(max_length=255, blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_y_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_n_amount_one = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    beizhun = models.CharField(max_length=255, blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    factory_make_id = models.IntegerField(blank=True, null=True)
    sample_static_id = models.IntegerField(blank=True, null=True)
    samp_info_id = models.IntegerField(blank=True, null=True)
    pay_custom = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sample_pay_info_list'


class SamplePayStatic(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    pay_custom = models.CharField(max_length=255, blank=True, null=True)
    pay_comment = models.CharField(max_length=255, blank=True, null=True)
    price_type = models.CharField(max_length=255, blank=True, null=True)
    pay_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_num = models.IntegerField(blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    finish_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sure = models.IntegerField(blank=True, null=True)
    is_finish_pay = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=255, blank=True, null=True)
    fee_amount = models.CharField(max_length=255, blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    fee_no_status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sample_pay_static'


class SampleType(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    sample_type_zh = models.CharField(max_length=100)
    sample_type_en = models.CharField(max_length=100)
    active = models.SmallIntegerField()
    balance = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sample_type'


class ShortShip(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    short_num = models.CharField(max_length=100)
    defalut = models.SmallIntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'short_ship'


class SingleSet(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    customer_type_id = models.IntegerField()
    prefix_name = models.CharField(max_length=25)
    time_type = models.SmallIntegerField()
    code_sign_start = models.CharField(max_length=25)
    code_number_start = models.CharField(max_length=25)
    type_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'single_set'


class Size(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    size = models.CharField(max_length=25)
    goods_size_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'size'


class SocialInsurance(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    social_insurance_level = models.CharField(max_length=255, blank=True, null=True)
    social_insurance_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    social_insurance_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    merchant_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'social_insurance'


class SubColour(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    sub_colour_name = models.CharField(max_length=25)
    colour_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sub_colour'


class SubSpecs(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    sub_specs_name = models.CharField(max_length=25)
    specs_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sub_specs'


class Submission(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    kuan_hao = models.CharField(max_length=255, blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True, null=True)
    start_num = models.CharField(max_length=255, blank=True, null=True)
    end_num = models.CharField(max_length=255, blank=True, null=True)
    box_num = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    size1 = models.CharField(max_length=255, blank=True, null=True)
    size2 = models.CharField(max_length=255, blank=True, null=True)
    size3 = models.CharField(max_length=255, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    submis_people = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'submission'


class SubmissionInfo(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    order_line_id = models.IntegerField(blank=True, null=True)
    info = models.CharField(max_length=255, blank=True, null=True)
    factory_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'submission_info'


class Surplu(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    surplu_level = models.CharField(max_length=255, blank=True, null=True)
    surplu_company = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surplu_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    merchant_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'surplu'


class WarehouseClassification(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)
    warehouse_name = models.CharField(max_length=25)
    method_id = models.IntegerField()
    active = models.SmallIntegerField()
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'warehouse_classification'


class ZToken(models.Model):
    create_time = models.DateTimeField(blank=True, null=True)
    user = models.CharField(max_length=255, blank=True, null=True)
    pwd = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    archi_list = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'z_token'

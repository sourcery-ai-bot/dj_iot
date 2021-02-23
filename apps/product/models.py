from utils.basemodel import BaseModel
from django.db import models
from user.models import User


class Product(BaseModel):
    product_name = models.CharField(max_length=125, default='', null=False, blank=False, verbose_name='产品名称')

    class Meta:
        db_table = 'tb_product'
        verbose_name = '产品'
        verbose_name_plural = verbose_name


class ProdPartner(BaseModel):
    pro_uuid = models.CharField(max_length=125, unique=True, default='', null=False, blank=False, verbose_name='uuid')
    pro_user = models.ManyToManyField(User, related_name='product', blank=True, verbose_name=u'参与用户')
    pro_create = models.ForeignKey(User, related_name='product_create', null=True, blank=True, verbose_name=u'创建者')

    class Meta:
        db_table = 'tb_prodpartner'
        verbose_name = '产品参与'
        verbose_name_plural = verbose_name


class FirmwareProduct(BaseModel):
    uuid_ascii_code = models.CharField(max_length=11, null=False, default='user_submit', verbose_name='升级码')
    product_project_num = models.CharField(max_length=64, null=False, default='', verbose_name='项目号')
    product_name = models.CharField(max_length=32, null=False, default='', verbose_name='产品型号')
    product_series = models.CharField(max_length=32, null=True, blank=True, default='', verbose_name='产品系列')
    offered_by = models.CharField(max_length=32, null=False, default='Aputure', verbose_name='公司')
    product_updated_admin_name = models.CharField(max_length=32, null=False, default='', verbose_name='最后更新人')
    submit_user = models.ForeignKey(User, related_name='product_submit', db_index=True, verbose_name='提交人员', null=True,
                                    on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_firmware_product'
        verbose_name = '固件产品'
        verbose_name_plural = verbose_name

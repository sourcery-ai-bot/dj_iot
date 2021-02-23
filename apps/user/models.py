from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.basemodel import BaseModel


class Department(BaseModel):
    department_name = models.CharField(max_length=125, default='', unique=True, null=False, blank=False,
                                       verbose_name='部门名称')

    class Meta:
        db_table = 'tb_department'
        verbose_name = '部门'
        verbose_name_plural = verbose_name


class User(AbstractUser):
    """用户模型类"""
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    sidus_avatar = models.CharField(max_length=125, default='', null=True, blank=True, verbose_name='Sidus头像')
    avatar_color = models.CharField(max_length=125, default='', null=True, blank=True, verbose_name='头像颜色')
    sidus_id = models.IntegerField(null=True, blank=True, verbose_name='id')
    sidus_token = models.CharField(max_length=256, default='', null=True, blank=True, verbose_name='Sidus token')
    department = models.ManyToManyField(Department, db_index=True, verbose_name='部门', related_name='users', null=True,
                                        blank=True)

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Role(BaseModel):
    role_name = models.CharField(max_length=125, unique=True, null=False, blank=False, verbose_name=u'角色名称')
    users = models.ManyToManyField(User, related_name='roles', blank=True,
                                   verbose_name=u'用户角色')
    describe = models.CharField(max_length=256, default='', null=True, blank=True, verbose_name=u'角色描述')

    class Meta:
        db_table = 'tb_role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name


class RequestInfo(BaseModel):
    user = models.OneToOneField(User, db_index=True, verbose_name='user',
                                related_name='request_info', default=None, null=True, blank=True, unique=True)
    department = models.CharField(max_length=125, null=True, blank=True, verbose_name=u'部门名称')
    status = models.IntegerField(null=True, blank=True, default=0, verbose_name='status')

    class Meta:
        db_table = 'tb_Requestinfo'
        verbose_name = '信息'
        verbose_name_plural = verbose_name

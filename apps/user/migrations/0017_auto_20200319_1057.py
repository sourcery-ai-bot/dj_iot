# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-03-19 02:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_auto_20200318_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='department_name',
            field=models.CharField(default='', max_length=125, unique=True, verbose_name='部门名称'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-03-30 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_auto_20200328_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prodpartner',
            name='pro_uuid',
            field=models.CharField(default='', max_length=125, unique=True, verbose_name='uuid'),
        ),
    ]

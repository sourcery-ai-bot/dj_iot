# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-03-17 03:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_auto_20200317_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sidus_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='id'),
        ),
        migrations.AddField(
            model_name='user',
            name='sidus_token',
            field=models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='Sidus token'),
        ),
    ]

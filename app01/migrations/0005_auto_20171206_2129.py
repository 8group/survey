# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-06 21:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_auto_20171206_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveyinfo',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.UserInfo'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-07 16:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_meetingroom_reserverecord'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reserverecord',
            unique_together=set([('meetingroom', 'date', 'phase')]),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-12 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordinaryPython36', '0025_channel_is_system_channel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='is_system_channel',
            field=models.BooleanField(),
        ),
    ]

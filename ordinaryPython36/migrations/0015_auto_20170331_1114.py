# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-31 11:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordinaryPython36', '0014_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publisher',
            name='logo',
            field=models.URLField(null=True),
        ),
    ]

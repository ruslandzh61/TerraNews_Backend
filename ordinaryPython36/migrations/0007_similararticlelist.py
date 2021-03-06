# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 14:55
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        ('ordinaryPython36', '0006_auto_20170214_0921'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimilarArticleList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similar_articles', models.TextField(validators=django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\ \\d+)*\\Z', 32), code='invalid', message=None))),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ordinaryPython36.Article')),
            ],
        ),
    ]

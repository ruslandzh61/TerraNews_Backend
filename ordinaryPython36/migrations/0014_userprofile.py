# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-30 10:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordinaryPython36', '0013_auto_20170318_0431'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.TextField(unique=True)),
                ('name', models.TextField(max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('picture', models.URLField(null=True)),
            ],
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-07 03:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ordinaryPython36', '0015_auto_20170331_1114'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserArticleInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_accessed', models.DateTimeField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ordinaryPython36.Article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ordinaryPython36.UserProfile')),
            ],
        ),
    ]
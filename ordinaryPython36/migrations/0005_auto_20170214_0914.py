# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 09:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ordinaryPython36', '0004_auto_20170214_0517'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('name', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ordinaryPython36.Category')),
            ],
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='article',
            name='feed',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ordinaryPython36.Feed'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-22 17:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ordinaryPython36', '0023_delete_tagchannel'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.TextField(max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_removed', models.DateTimeField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ordinaryPython36.UserProfile')),
            ],
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-24 13:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0004_logbook_organisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='logbook',
            name='name_slug',
            field=models.SlugField(blank=True, default=None),
        ),
    ]
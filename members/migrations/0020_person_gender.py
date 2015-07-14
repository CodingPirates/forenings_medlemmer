# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0019_auto_20150713_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='gender',
            field=models.CharField(verbose_name='Køn', null=True, max_length=20, choices=[('MA', 'Dreng'), ('FM', 'Pige')], default=None),
        ),
    ]

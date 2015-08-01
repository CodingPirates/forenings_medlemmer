# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0046_auto_20150801_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='max_age',
            field=models.PositiveIntegerField(default=17, verbose_name='Maximum Alder'),
        ),
        migrations.AddField(
            model_name='activity',
            name='min_age',
            field=models.PositiveIntegerField(default=7, verbose_name='Minimum Alder'),
        ),
    ]

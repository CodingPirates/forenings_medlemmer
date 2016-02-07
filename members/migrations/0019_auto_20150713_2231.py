# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0018_auto_20150713_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='added',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Tilføjet'),
        ),
    ]

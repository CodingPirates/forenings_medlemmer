# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0052_auto_20150804_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='price',
            field=models.IntegerField(verbose_name='Pris (øre)', default=0),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='end',
            field=models.DateField(verbose_name='Slut'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='activity',
            name='start',
            field=models.DateField(verbose_name='Start'),
            preserve_default=True,
        ),
    ]

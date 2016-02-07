# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0047_auto_20150801_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='description',
            field=models.TextField(verbose_name='Beskrivelse'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='max_participants',
            field=models.PositiveIntegerField(default=30, verbose_name='Max deltagere'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='responsible_name',
            field=models.CharField(max_length=200, verbose_name='Ansvarlig'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0053_auto_20150804_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityparticipant',
            name='added_dtm',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Tilmeldt'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0055_auto_20150818_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='refunded_dtm',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Refunderet'),
        ),
    ]

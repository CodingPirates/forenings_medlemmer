# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0057_activity_price_in_dkk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='price',
        ),
    ]

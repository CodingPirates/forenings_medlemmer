# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0015_auto_20150709_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]

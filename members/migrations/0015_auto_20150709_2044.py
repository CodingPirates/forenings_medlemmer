# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0014_auto_20150709_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]

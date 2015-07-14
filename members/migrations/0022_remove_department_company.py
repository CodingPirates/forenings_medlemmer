# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0021_department_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='company',
        ),
    ]

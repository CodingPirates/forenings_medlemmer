# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0037_auto_20150724_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityinvite',
            name='rejected_dtm',
            field=models.DateField(null=True, verbose_name='Afslået'),
        ),
    ]

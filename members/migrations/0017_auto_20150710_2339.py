# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0016_auto_20150709_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='updated_dtm',
            field=models.DateTimeField(verbose_name='Sidst redigeret', auto_now=True),
        ),
    ]

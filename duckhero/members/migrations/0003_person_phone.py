# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20150221_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='phone',
            field=models.CharField(verbose_name='Telefon', max_length=50, blank=True),
            preserve_default=True,
        ),
    ]

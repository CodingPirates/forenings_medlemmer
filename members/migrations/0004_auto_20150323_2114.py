# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_auto_20150323_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailitem',
            name='sent_dtm',
            field=models.DateTimeField(null=True, verbose_name='Sendt', blank=True, editable=False),
            preserve_default=True,
        ),
    ]

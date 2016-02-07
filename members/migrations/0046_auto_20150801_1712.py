# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0045_auto_20150725_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='person',
            field=models.ForeignKey(to='members.Person', unique=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='person',
            name='membertype',
            field=models.CharField(verbose_name='Type', choices=[('PA', 'Forælder'), ('GU', 'Værge'), ('CH', 'Barn'), ('NA', 'Anden')], default='PA', max_length=2),
        ),
    ]

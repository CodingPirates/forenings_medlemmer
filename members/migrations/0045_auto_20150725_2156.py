# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0044_auto_20150725_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminuserinformation',
            name='department',
            field=models.ForeignKey(to='members.Department', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='member',
            name='person',
            field=models.ForeignKey(to='members.Person', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='quickpaytransaction',
            name='refunding',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='members.QuickpayTransaction', null=True),
        ),
    ]

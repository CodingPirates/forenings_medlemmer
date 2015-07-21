# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0032_auto_20150722_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quickpaytransaction',
            name='refunding',
            field=models.ForeignKey(to='members.QuickpayTransaction', null=True, default=None),
        ),
        migrations.AlterField(
            model_name='quickpaytransaction',
            name='transaction_id',
            field=models.IntegerField(default=None, null=True, verbose_name='Transaktions ID'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0043_payment_activityparticipant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='activity',
            field=models.ForeignKey(blank=True, to='members.Activity', on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='activityparticipant',
            field=models.ForeignKey(blank=True, to='members.ActivityParticipant', on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='members.Family'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='person',
            field=models.ForeignKey(blank=True, to='members.Person', on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
    ]

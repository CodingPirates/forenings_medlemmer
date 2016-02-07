# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0050_auto_20150801_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='anounced_activity_participant',
            field=models.ForeignKey(null=True, to='members.ActivityParticipant'),
        ),
    ]

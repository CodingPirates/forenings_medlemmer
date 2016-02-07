# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0051_notification_anounced_activity_participant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='city',
            field=models.CharField(verbose_name='By', blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='housenumber',
            field=models.CharField(verbose_name='Husnummer', blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='person',
            name='streetname',
            field=models.CharField(verbose_name='Vejnavn', blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='zipcode',
            field=models.CharField(verbose_name='Postnummer', blank=True, max_length=4),
        ),
        migrations.AlterUniqueTogether(
            name='activityinvite',
            unique_together=set([('activity', 'person')]),
        ),
        migrations.AlterUniqueTogether(
            name='activityparticipant',
            unique_together=set([('activity', 'member')]),
        ),
    ]

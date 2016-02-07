# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0036_auto_20150724_0057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityinvite',
            name='unique',
        ),
        migrations.AddField(
            model_name='activity',
            name='signup_closing',
            field=models.DateField(verbose_name='Tilmelding lukker', null=True),
        ),
        migrations.AddField(
            model_name='activityinvite',
            name='expire_dtm',
            field=models.DateField(verbose_name='Udløber', default=datetime.datetime(2015, 7, 24, 14, 4, 49, 698757, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activityinvite',
            name='invite_dtm',
            field=models.DateField(verbose_name='Inviteret', default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(max_length=2, choices=[('CA', 'Kontant betaling'), ('BA', 'Bankoverførsel'), ('CC', 'Kreditkort'), ('RE', 'Refunderet'), ('OT', 'Andet')], verbose_name='Type', default='CA'),
        ),
    ]

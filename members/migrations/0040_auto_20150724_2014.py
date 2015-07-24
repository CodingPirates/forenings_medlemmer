# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0039_auto_20150724_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='price',
            field=models.IntegerField(default=None, null=True, blank=True, verbose_name='Pris (øre)'),
        ),
        migrations.AlterField(
            model_name='member',
            name='member_since',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Indmeldt'),
        ),
        migrations.AlterField(
            model_name='member',
            name='member_until',
            field=models.DateField(default=None, null=True, blank=True, verbose_name='Udmeldt'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='activity',
            field=models.ForeignKey(to='members.Activity', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='body_text',
            field=models.TextField(verbose_name='Beskrivelse'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='confirmed_dtm',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Bekræftet'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='person',
            field=models.ForeignKey(to='members.Person', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='rejected_dtm',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Bekræftet'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='rejected_message',
            field=models.TextField(null=True, blank=True, verbose_name='Afvist årsag'),
        ),
    ]

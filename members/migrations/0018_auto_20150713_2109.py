# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0017_auto_20150710_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='door',
            field=models.CharField(max_length=10, verbose_name='Dør', blank=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='floor',
            field=models.CharField(max_length=10, verbose_name='Etage', blank=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='housenumber',
            field=models.CharField(max_length=10, verbose_name='Husnummer'),
        ),
        migrations.AlterField(
            model_name='department',
            name='open_hours',
            field=models.CharField(max_length=200, verbose_name='Åbningstid', blank=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='placename',
            field=models.CharField(max_length=200, verbose_name='Stednavn', blank=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='responsible_name',
            field=models.CharField(max_length=200, verbose_name='Afdelingsleder', blank=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='zipcode',
            field=models.CharField(max_length=10, verbose_name='Postnummer'),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='department',
            field=models.ForeignKey(blank=True, null=True, to='members.Department'),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='family',
            field=models.ForeignKey(blank=True, null=True, to='members.Family'),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='person',
            field=models.ForeignKey(blank=True, null=True, to='members.Person'),
        ),
    ]

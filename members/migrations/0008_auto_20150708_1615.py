# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_auto_20150707_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='city',
            field=models.CharField(verbose_name='By', default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='dawa_id',
            field=models.CharField(verbose_name='DAWA id', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='door',
            field=models.CharField(verbose_name='Dør', max_length=5, blank=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='floor',
            field=models.CharField(verbose_name='Etage', max_length=3, blank=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='housenumber',
            field=models.CharField(verbose_name='Husnummer', default='', max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='open_hours',
            field=models.CharField(verbose_name='Tidspunkt', max_length=4, blank=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='placename',
            field=models.CharField(verbose_name='Stednavn', default='', max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='responsible_contact',
            field=models.EmailField(verbose_name='E-mail', max_length=254, blank=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='responsible_name',
            field=models.CharField(verbose_name='Afdelingsleder', max_length=4, blank=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='streetname',
            field=models.CharField(verbose_name='Vejnavn', default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='zipcode',
            field=models.CharField(verbose_name='Postnummer', default='', max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activityparticipant',
            name='note',
            field=models.TextField(verbose_name='Besked / Note til arrangement', blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='city',
            field=models.CharField(verbose_name='By', default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='department',
            name='dawa_id',
            field=models.CharField(verbose_name='DAWA id', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='description',
            field=models.TextField(verbose_name='Beskrivelse af afdeling', blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='door',
            field=models.CharField(verbose_name='Dør', max_length=5, blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='floor',
            field=models.CharField(verbose_name='Etage', max_length=3, blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='housenumber',
            field=models.CharField(verbose_name='Husnummer', default='', max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='department',
            name='open_hours',
            field=models.CharField(verbose_name='Åbningstid', max_length=4, blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='placename',
            field=models.CharField(verbose_name='Stednavn', max_length=4, blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='responsible_contact',
            field=models.EmailField(verbose_name='E-mail', max_length=254, blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='responsible_name',
            field=models.CharField(verbose_name='Afdelingsleder', max_length=4, blank=True),
        ),
        migrations.AddField(
            model_name='department',
            name='streetname',
            field=models.CharField(verbose_name='Vejnavn', default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='department',
            name='zipcode',
            field=models.CharField(verbose_name='Postnummer', default='', max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='photo_permission',
            field=models.CharField(verbose_name='Fotogri tilladelse', choices=[('OK', 'Tilladelse givet'), ('ND', 'Ikke taget stilling'), ('NO', 'Ikke tilladt')], default='ND', max_length=2),
        ),
    ]

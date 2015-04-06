# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_auto_20150323_2114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='street',
        ),
        migrations.RemoveField(
            model_name='person',
            name='zipcity',
        ),
        migrations.AddField(
            model_name='person',
            name='door',
            field=models.CharField(max_length=5, verbose_name=b'D\xc3\xb8r', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='floor',
            field=models.CharField(max_length=3, verbose_name=b'Etage', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='housenumber',
            field=models.CharField(default='1', max_length=5, verbose_name=b'Husnummer'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='streetname',
            field=models.CharField(default='vejnavn', max_length=200, verbose_name=b'Vejnavn'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='zipcode',
            field=models.CharField(default=1234, max_length=4, verbose_name=b'Postnummer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='body',
            field=models.CharField(max_length=10000, verbose_name=b'Indhold', blank=True),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='sent_dtm',
            field=models.DateTimeField(null=True, verbose_name=b'Sendt', blank=True),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='subject',
            field=models.CharField(max_length=200, verbose_name=b'Emne', blank=True),
        ),
        migrations.AlterField(
            model_name='family',
            name='email',
            field=models.EmailField(unique=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='has_certificate',
            field=models.DateField(null=True, verbose_name=b'B\xc3\xb8rneattest', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='membertype',
            field=models.CharField(default=b'PA', max_length=2, verbose_name=b'Type', choices=[(b'PA', b'For\xc3\xa6lder'), (b'GU', b'V\xc3\xa6rge'), (b'CH', b'Barn'), (b'NA', b'Frivillig')]),
        ),
        migrations.AlterField(
            model_name='person',
            name='on_waiting_list_since',
            field=models.DateField(auto_now_add=True, verbose_name=b'Tilf\xc3\xb8jet'),
        ),
    ]

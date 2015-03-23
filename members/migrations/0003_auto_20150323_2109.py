# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20150228_2210'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_dtm', models.DateTimeField(verbose_name='Oprettet', auto_now_add=True)),
                ('subject', models.CharField(editable=False, verbose_name='Emne', max_length=200, blank=True)),
                ('body', models.CharField(editable=False, verbose_name='Indhold', max_length=10000, blank=True)),
                ('sent_dtm', models.DateTimeField(editable=False, verbose_name='Sendt', blank=True)),
                ('send_error', models.CharField(editable=False, verbose_name='Fejl i afsendelse', max_length=200, blank=True)),
                ('activity', models.ForeignKey(to='members.Activity', null=True)),
                ('person', models.ForeignKey(to='members.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='person',
            name='membertype',
            field=models.CharField(choices=[('PA', 'Forælder'), ('GU', 'Værge'), ('CH', 'Barn'), ('NA', 'Frivillig')], verbose_name='Type', default='PA', max_length=2),
            preserve_default=True,
        ),
    ]

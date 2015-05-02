# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20150403_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created_dtm', models.DateTimeField(verbose_name='Oprettet', auto_now_add=True)),
                ('body', models.TextField(verbose_name='Indhold')),
                ('family', models.ForeignKey(to='members.Family')),
            ],
            options={
                'verbose_name': 'Journal',
                'verbose_name_plural': 'Journaler',
            },
        ),
        migrations.AddField(
            model_name='person',
            name='city',
            field=models.CharField(max_length=200, verbose_name='By', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='body',
            field=models.CharField(max_length=10000, verbose_name='Indhold', blank=True),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='sent_dtm',
            field=models.DateTimeField(null=True, verbose_name='Sendt', blank=True),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='subject',
            field=models.CharField(max_length=200, verbose_name='Emne', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='door',
            field=models.CharField(max_length=5, verbose_name='Dør', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='floor',
            field=models.CharField(max_length=3, verbose_name='Etage', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='has_certificate',
            field=models.DateField(null=True, verbose_name='Børneattest', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='housenumber',
            field=models.CharField(max_length=5, verbose_name='Husnummer'),
        ),
        migrations.AlterField(
            model_name='person',
            name='membertype',
            field=models.CharField(max_length=2, verbose_name='Type', choices=[('PA', 'Forælder'), ('GU', 'Værge'), ('CH', 'Barn'), ('NA', 'Frivillig')], default='PA'),
        ),
        migrations.AlterField(
            model_name='person',
            name='on_waiting_list_since',
            field=models.DateField(verbose_name='Tilføjet', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='streetname',
            field=models.CharField(max_length=200, verbose_name='Vejnavn'),
        ),
        migrations.AlterField(
            model_name='person',
            name='zipcode',
            field=models.CharField(max_length=4, verbose_name='Postnummer'),
        ),
        migrations.AddField(
            model_name='journal',
            name='person',
            field=models.ForeignKey(null=True, to='members.Person'),
        ),
    ]

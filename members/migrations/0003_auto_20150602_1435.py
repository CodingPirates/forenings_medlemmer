# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20150525_0231'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('idname', models.SlugField(verbose_name='Unikt reference navn', unique=True)),
                ('created_dtm', models.DateTimeField(verbose_name='Oprettet', auto_now_add=True)),
                ('name', models.CharField(max_length=200, verbose_name='Skabelon navn')),
                ('description', models.CharField(max_length=200, verbose_name='Skabelon beskrivelse')),
                ('from_address', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200, verbose_name='Emne')),
                ('body_html', models.TextField(blank=True, verbose_name='HTML Indhold')),
                ('body_text', models.TextField(blank=True, verbose_name='Text Indhold')),
            ],
            options={
                'verbose_name': 'Email Template',
                'verbose_name_plural': 'Email Templates',
            },
        ),
        migrations.RemoveField(
            model_name='emailitem',
            name='body',
        ),
        migrations.AddField(
            model_name='emailitem',
            name='body_html',
            field=models.TextField(blank=True, verbose_name='HTML Indhold'),
        ),
        migrations.AddField(
            model_name='emailitem',
            name='body_text',
            field=models.TextField(blank=True, verbose_name='Text Indhold'),
        ),
        migrations.AddField(
            model_name='emailitem',
            name='department',
            field=models.ForeignKey(null=True, to='members.Department'),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='sent_dtm',
            field=models.DateTimeField(blank=True, verbose_name='Sendt tidstempel', null=True),
        ),
        migrations.AddField(
            model_name='emailitem',
            name='template',
            field=models.ForeignKey(null=True, to='members.EmailTemplate'),
        ),
    ]

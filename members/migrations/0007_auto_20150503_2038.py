# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_auto_20150501_2033'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaitingList',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('on_waiting_list_since', models.DateField(null=True, verbose_name='Tilføjet', blank=True)),
            ],
            options={
                'ordering': ['on_waiting_list_since'],
                'verbose_name_plural': 'På venteliste',
            },
        ),
        migrations.RenameField(
            model_name='person',
            old_name='on_waiting_list_since',
            new_name='added',
        ),
        migrations.RemoveField(
            model_name='person',
            name='on_waiting_list',
        ),
        migrations.AddField(
            model_name='department',
            name='has_waiting_list',
            field=models.BooleanField(verbose_name='Venteliste', default=False),
        ),
        migrations.AddField(
            model_name='waitinglist',
            name='department',
            field=models.ForeignKey(to='members.Department'),
        ),
        migrations.AddField(
            model_name='waitinglist',
            name='person',
            field=models.ForeignKey(to='members.Person'),
        ),
    ]

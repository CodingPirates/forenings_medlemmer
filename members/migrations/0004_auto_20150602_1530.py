# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.fields
import datetime
import uuid
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_auto_20150602_1435'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('update_info_dtm', models.DateTimeField(verbose_name='Bedt om opdatering af info', null=True, blank=True)),
                ('warned_deletion_info_dtm', models.DateTimeField(verbose_name='Advaret om sletning fra liste', null=True, blank=True)),
                ('anounced_activity', models.ForeignKey(to='members.Activity', null=True)),
                ('anounced_department', models.ForeignKey(to='members.Department', null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='emailtemplate',
            options={'verbose_name': 'Email Skabelon', 'verbose_name_plural': 'Email Skabeloner'},
        ),
        migrations.RenameField(
            model_name='emailtemplate',
            old_name='created_dtm',
            new_name='updated_dtm',
        ),
        migrations.AddField(
            model_name='emailitem',
            name='bounce_token',
            field=django.db.models.fields.UUIDField(editable=False, default=uuid.uuid4, blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='email',
            field=models.ForeignKey(to='members.EmailItem'),
        ),
        migrations.AddField(
            model_name='notification',
            name='family',
            field=models.ForeignKey(to='members.Family'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['start_date'], 'verbose_name': 'aktivitet', 'verbose_name_plural': 'Aktiviteter'},
        ),
        migrations.RenameField(
            model_name='activity',
            old_name='end',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='activity',
            old_name='start',
            new_name='start_date',
        ),
    ]

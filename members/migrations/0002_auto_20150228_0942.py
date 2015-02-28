# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='on_waitingList',
            new_name='on_waiting_list',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='on_waitingList_since',
            new_name='on_waiting_list_since',
        ),
    ]

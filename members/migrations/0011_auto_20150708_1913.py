from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0010_auto_20150708_1905'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='on_waiting_list',
        ),
        migrations.RemoveField(
            model_name='person',
            name='on_waiting_list_since',
        ),
    ]

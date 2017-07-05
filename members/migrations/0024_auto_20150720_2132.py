from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0023_auto_20150714_2224'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'permissions': (('view_full_address', 'Can view persons full address + phonenumber + email'),), 'ordering': ['name'], 'verbose_name_plural': 'Personer'},
        ),
    ]

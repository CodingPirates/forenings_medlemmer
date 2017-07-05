from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0026_auto_20150720_2255'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'verbose_name_plural': 'Familier', 'permissions': (('view_family_unique', 'Can view family UUID field (password) - gives access to address'),), 'verbose_name': 'familie'},
        ),
    ]

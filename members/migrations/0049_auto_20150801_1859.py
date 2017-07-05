from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0048_auto_20150801_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='members.Person'),
        ),
    ]

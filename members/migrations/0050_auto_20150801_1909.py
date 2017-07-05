from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0049_auto_20150801_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityparticipant',
            name='activity',
            field=models.ForeignKey(to='members.Activity', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='member',
            name='department',
            field=models.ForeignKey(to='members.Department', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]

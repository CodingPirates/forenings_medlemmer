from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_auto_20150707_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='updated',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Opdateret'),
        ),
        migrations.AlterField(
            model_name='person',
            name='updated',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Opdateret'),
        ),
    ]

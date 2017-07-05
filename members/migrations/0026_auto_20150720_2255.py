from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0025_auto_20150720_2254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='description',
            field=models.TextField(blank=True, verbose_name='Beskrivelse'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='instructions',
            field=models.TextField(blank=True, verbose_name='Tilmeldings instruktioner'),
        ),
    ]

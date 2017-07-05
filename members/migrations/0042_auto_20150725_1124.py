from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0041_auto_20150724_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='family',
            name='contact_visible',
        ),
        migrations.RemoveField(
            model_name='person',
            name='photo_permission',
        ),
        migrations.AddField(
            model_name='activityparticipant',
            name='contact_visible',
            field=models.BooleanField(default=False, verbose_name='Kontaktoplysninger synlige for andre holddeltagere'),
        ),
        migrations.AddField(
            model_name='activityparticipant',
            name='photo_permission',
            field=models.CharField(choices=[('OK', 'Tilladelse givet'), ('NO', 'Ikke tilladt')], max_length=2, default='NO', verbose_name='Foto tilladelse'),
        ),
    ]

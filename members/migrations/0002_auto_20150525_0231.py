from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='birthday',
            field=models.DateField(null=True, verbose_name='Fødselsdag', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='dawa_id',
            field=models.CharField(verbose_name='DAWA id', max_length=200, blank=True),
        ),
    ]

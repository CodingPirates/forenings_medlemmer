from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0020_person_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='company',
            field=models.CharField(verbose_name='Firma', max_length=200, blank=True),
        ),
    ]

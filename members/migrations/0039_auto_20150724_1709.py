# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0038_activityinvite_rejected_dtm'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='contact_visible',
            field=models.BooleanField(verbose_name='Kontaktoplysninger synlige for andre holddeltagere', default=False),
        ),
        migrations.AlterField(
            model_name='activityinvite',
            name='rejected_dtm',
            field=models.DateField(verbose_name='Afslået', null=True, blank=True),
        ),
    ]

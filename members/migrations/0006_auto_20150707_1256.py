from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20150610_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='updated',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2015, 7, 7, 10, 56, 5, 790785, tzinfo=utc), verbose_name='Opdateret'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='updated',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2015, 7, 7, 10, 56, 14, 542582, tzinfo=utc), verbose_name='Opdateret'),
            preserve_default=False,
        ),
    ]

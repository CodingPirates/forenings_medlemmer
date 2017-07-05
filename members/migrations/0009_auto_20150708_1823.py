from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_auto_20150708_1615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='family',
            name='updated',
        ),
        migrations.RemoveField(
            model_name='person',
            name='updated',
        ),
        migrations.AddField(
            model_name='activity',
            name='updated_dtm',
            field=models.DateTimeField(verbose_name='Opdateret', auto_now=True, default=datetime.datetime(2015, 7, 8, 16, 23, 28, 408049, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='department',
            name='updated_dtm',
            field=models.DateTimeField(verbose_name='Opdateret', auto_now=True, default=datetime.datetime(2015, 7, 8, 16, 23, 33, 527851, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='family',
            name='updated_dtm',
            field=models.DateTimeField(verbose_name='Opdateret', auto_now=True, default=datetime.datetime(2015, 7, 8, 16, 23, 38, 951920, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='updated_dtm',
            field=models.DateTimeField(verbose_name='Opdateret', auto_now=True, default=datetime.datetime(2015, 7, 8, 16, 23, 42, 568027, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='member_since',
            field=models.DateTimeField(verbose_name='Indmeldt', default=django.utils.timezone.now),
        ),
    ]

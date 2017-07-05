from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0011_auto_20150708_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='open_invite',
            field=models.BooleanField(verbose_name='Fri tilmelding', default=False),
        ),
    ]

from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0012_activity_open_invite'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='member_until',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Udmeldt', default=None),
        ),
    ]

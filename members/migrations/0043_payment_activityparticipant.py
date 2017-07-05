from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0042_auto_20150725_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='activityparticipant',
            field=models.ForeignKey(to='members.ActivityParticipant', blank=True, null=True),
        ),
    ]

from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0054_activityparticipant_added_dtm'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'permissions': (('view_full_address', 'Can view persons full address + phonenumber + email'),), 'verbose_name_plural': 'Personer', 'ordering': ['added']},
        ),
        migrations.AddField(
            model_name='payment',
            name='cancelled_dtm',
            field=models.DateTimeField(verbose_name='Annulleret', blank=True, null=True),
        ),
    ]

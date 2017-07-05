from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0031_auto_20150722_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='activity',
            field=models.ForeignKey(to='members.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='person',
            field=models.ForeignKey(to='members.Person', null=True),
        ),
    ]

from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0030_auto_20150721_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='confirmed_dtm',
            field=models.DateTimeField(verbose_name='Bekræftet', null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='rejected_dtm',
            field=models.DateTimeField(verbose_name='Bekræftet', null=True),
        ),
    ]

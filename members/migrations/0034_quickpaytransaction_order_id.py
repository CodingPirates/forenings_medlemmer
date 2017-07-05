from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0033_auto_20150722_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='quickpaytransaction',
            name='order_id',
            field=models.CharField(verbose_name='Quickpay order id', editable=False, max_length=20, blank=True),
        ),
    ]

from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0034_quickpaytransaction_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quickpaytransaction',
            name='order_id',
            field=models.CharField(blank=True, unique=True, max_length=20, editable=False, verbose_name='Quickpay order id'),
        ),
    ]

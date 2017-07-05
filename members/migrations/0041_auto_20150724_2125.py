from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0040_auto_20150724_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='rejected_dtm',
            field=models.DateTimeField(null=True, verbose_name='Afvist', blank=True),
        ),
        migrations.AlterField(
            model_name='quickpaytransaction',
            name='link_url',
            field=models.CharField(blank=True, max_length=512, verbose_name='Link til Quickpay formular'),
        ),
        migrations.AlterField(
            model_name='quickpaytransaction',
            name='order_id',
            field=models.CharField(blank=True, unique=True, max_length=20, verbose_name='Quickpay order id'),
        ),
    ]

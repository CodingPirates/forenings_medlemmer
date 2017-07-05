from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0029_payment_quickpaytransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(max_length=2, verbose_name='Type', default='CA', choices=[('CA', 'Kontant betaling'), ('BA', 'Bankoverførsel'), ('CC', 'Kreditkort'), ('RE', 'Refunderet')]),
        ),
    ]

from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0056_payment_refunded_dtm'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='price_in_dkk',
            field=models.DecimalField(max_digits=10, verbose_name='Pris', decimal_places=2, default=300),
        ),
        migrations.RunSQL('UPDATE members_activity SET price_in_dkk = price / 100')
    ]

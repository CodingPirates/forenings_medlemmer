from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0058_remove_activity_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='created',
            field=models.DateField(verbose_name='Indmeldt', default=django.utils.timezone.datetime(year=2015, month=8, day=1)),
        ),
        migrations.AlterField(
            model_name='activity',
            name='price_in_dkk',
            field=models.DecimalField(verbose_name='Pris', default=500, max_digits=10, decimal_places=2),
        ),
    ]

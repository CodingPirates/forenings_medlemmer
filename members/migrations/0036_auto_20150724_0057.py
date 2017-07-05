from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0035_auto_20150722_0106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='door',
            field=models.CharField(verbose_name='Dør', blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='activity',
            name='floor',
            field=models.CharField(verbose_name='Etage', blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='activity',
            name='housenumber',
            field=models.CharField(verbose_name='Husnummer', max_length=200),
        ),
        migrations.AlterField(
            model_name='activity',
            name='responsible_name',
            field=models.CharField(verbose_name='Afdelingsleder', max_length=200),
        ),
    ]

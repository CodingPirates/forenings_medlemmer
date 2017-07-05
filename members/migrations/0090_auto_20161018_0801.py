# Generated by Django 1.9.1 on 2016-10-18 06:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0089_auto_20161017_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='brand',
            field=models.CharField(blank=True, default=None, max_length=200, null=True, verbose_name='Mærke'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='model',
            field=models.CharField(blank=True, default=None, max_length=200, null=True, verbose_name='Model'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='serial',
            field=models.CharField(blank=True, default=None, max_length=200, null=True, verbose_name='Serienummer'),
        ),
    ]

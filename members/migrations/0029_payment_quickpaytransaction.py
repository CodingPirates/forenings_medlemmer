# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0028_adminuserinformation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('added', models.DateTimeField(verbose_name='Tilføjet', default=django.utils.timezone.now)),
                ('payment_type', models.CharField(verbose_name='Type', default='CA', choices=[('CA', 'Kontant betaling'), ('BA', 'Bankoverførsel'), ('CC', 'Kreditkort'), ('RE', 'Refunderet'), ('DE', 'Debitering')], max_length=2)),
                ('body_text', models.TextField(verbose_name='Beskrivelse', blank=True)),
                ('amount_ore', models.IntegerField(verbose_name='Beløb i øre', default=0)),
                ('confirmed_dtm', models.DateTimeField(verbose_name='Bekræftet', blank=True)),
                ('rejected_dtm', models.DateTimeField(verbose_name='Bekræftet', blank=True)),
                ('rejected_message', models.TextField(verbose_name='Afvist årsag', blank=True)),
                ('activity', models.ForeignKey(to='members.Activity', blank=True)),
                ('family', models.ForeignKey(to='members.Family')),
                ('person', models.ForeignKey(to='members.Person', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuickpayTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('link_url', models.CharField(verbose_name='Link til Quickpay formular', editable=False, max_length=512, blank=True)),
                ('transaction_id', models.IntegerField(verbose_name='Transaktions ID')),
                ('amount_ore', models.IntegerField(verbose_name='Beløb i øre', default=0)),
                ('payment', models.ForeignKey(to='members.Payment')),
                ('refunding', models.ForeignKey(to='members.QuickpayTransaction')),
            ],
        ),
    ]

# Generated by Django 2.2.3 on 2019-07-31 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_newpaymenttemp'),
    ]

    operations = [
        migrations.AddField(
            model_name='newpaymenttemp',
            name='confirmed_dtm',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Bekræftet'),
        ),
        migrations.AddField(
            model_name='newpaymenttemp',
            name='rejected_dtm',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Afvist'),
        ),
        migrations.AddField(
            model_name='newpaymenttemp',
            name='old_pk',
            field=models.IntegerField(blank=True, null=True, verbose_name='Gammel primær nøgle')
        ),
        migrations.AlterField(
            model_name='newpaymenttemp',
            name='status',
            field=models.CharField(choices=[('NE', 'Ny transaktion'), ('CA', 'Annulleret'), ('RE', 'Refunderet')], default='NE', max_length=2, verbose_name='Status'),
        ),
    ]

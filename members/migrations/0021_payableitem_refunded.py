# Generated by Django 2.2.9 on 2020-03-22 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0020_auto_20200322_0324"),
    ]

    operations = [
        migrations.AddField(
            model_name="payableitem",
            name="refunded",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Refunderet"
            ),
        ),
    ]

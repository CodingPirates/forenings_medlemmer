# Generated by Django 3.0.4 on 2020-03-29 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0024_auto_20200328_0323"),
    ]

    operations = [
        migrations.AddField(
            model_name="payableitem",
            name="accepted",
            field=models.BooleanField(default=False, verbose_name="Accepteret"),
        ),
    ]

# Generated by Django 3.1.1 on 2021-03-23 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0027_auto_20210323_0925"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="activity",
            options={
                "ordering": ["-start_date", "department__address__zipcode"],
                "verbose_name": "Aktivitet",
                "verbose_name_plural": "Aktiviteter",
            },
        ),
    ]

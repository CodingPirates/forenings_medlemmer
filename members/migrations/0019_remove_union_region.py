# Generated by Django 2.2.9 on 2020-02-10 13:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0018_auto_20200130_1731"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="union",
            name="region",
        ),
    ]

# Generated by Django 4.1.4 on 2023-01-23 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0036_rename_founded_union_founded_at_union_closed_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activityparticipant",
            name="note",
            field=models.TextField(
                blank=True, verbose_name="Besked / Note til aktivitet"
            ),
        ),
    ]
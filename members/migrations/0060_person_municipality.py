# Generated by Django 4.2.16 on 2024-11-11 21:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0059_remove_person_municipality"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="municipality",
            field=models.ForeignKey(
                blank=True,
                default="",
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                to="members.municipality",
            ),
        ),
    ]
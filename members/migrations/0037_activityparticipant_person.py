# Generated by Django 4.1.6 on 2023-02-26 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0036_rename_founded_union_founded_at_union_closed_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="activityparticipant",
            name="person",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="members.person",
                verbose_name="Person",
            ),
        ),
    ]

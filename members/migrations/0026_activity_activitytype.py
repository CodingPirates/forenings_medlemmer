# Generated by Django 3.1.1 on 2021-03-22 22:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0025_activitytype"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="activitytype",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="members.activitytype",
            ),
        ),
    ]

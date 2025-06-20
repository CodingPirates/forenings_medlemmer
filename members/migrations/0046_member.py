# Generated by Django 4.2.2 on 2023-08-20 13:33

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0045_alter_activity_activitytype_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "member_since",
                    models.DateField(
                        default=datetime.datetime(
                            2023,
                            8,
                            20,
                            13,
                            33,
                            53,
                            638526,
                            tzinfo=datetime.timezone.utc,
                        ),
                        verbose_name="Medlemskab start",
                    ),
                ),
                (
                    "member_until",
                    models.DateField(
                        blank=True,
                        default=datetime.date(2023, 12, 31),
                        null=True,
                        verbose_name="Medlemskab slut",
                    ),
                ),
                (
                    "price_in_dkk",
                    models.DecimalField(
                        decimal_places=2,
                        default=75,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(75.0)],
                        verbose_name="Pris",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="members.person"
                    ),
                ),
                (
                    "union",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="members.union",
                        verbose_name="Forening",
                    ),
                ),
            ],
            options={
                "verbose_name": "Medlem",
                "verbose_name_plural": "Medlemmer",
            },
        ),
    ]

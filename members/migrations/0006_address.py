# Generated by Django 2.2.8 on 2019-12-30 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0005_payment_accepted_dtm"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
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
                ("streetname",),
                (
                    "housenumber",
                    models.CharField(max_length=5, verbose_name="Husnummer"),
                ),
                (
                    "floor",
                    models.CharField(
                        blank=True, max_length=10, null=True, verbose_name="Etage"
                    ),
                ),
                (
                    "door",
                    models.CharField(
                        blank=True, max_length=10, null=True, verbose_name="Dør"
                    ),
                ),
                ("city", models.CharField(max_length=200, verbose_name="By")),
                ("zipcode", models.CharField(max_length=4, verbose_name="Postnummer")),
                (
                    "municipality",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Kommune"
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                        verbose_name="Længdegrad",
                    ),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                        verbose_name="Breddegrad",
                    ),
                ),
                (
                    "dawa_id",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="DAWA id"
                    ),
                ),
            ],
            options={
                "ordering": ["zipcode"],
                "verbose_name": "Adresse",
                "verbose_name_plural": "Adresser",
            },
        ),
    ]

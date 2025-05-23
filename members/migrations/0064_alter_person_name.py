# Generated by Django 4.2.11 on 2025-02-23 12:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0063_merge_20241229_1529"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="name",
            field=models.CharField(
                max_length=200,
                validators=[
                    django.core.validators.RegexValidator(
                        "(^[A-Za-zÆØÅæøå]{3,16})([ ]{0,1})([A-Za-zÆØÅæøå]{3,16})?([ ]{0,1})?([A-Za-zÆØÅæøå]{3,16})?([ ]{0,1})?([A-Za-zÆØÅæøå]{3,16})([ ]{0,1})?([A-Za-zÆØÅæøå]{3,16})$",
                        message="Indtast et gyldigt navn bestående af fornavn og minimum et efternavn.",
                    )
                ],
                verbose_name="Navn",
            ),
        ),
    ]

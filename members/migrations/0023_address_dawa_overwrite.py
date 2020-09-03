# Generated by Django 3.1 on 2020-09-02 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0022_merge_20200526_1130"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="dawa_overwrite",
            field=models.BooleanField(
                default=False,
                help_text="Lader dig gemme en anden Længdegrad og breddegrad end den gemt i DAWA (hvor vi henter adressedata). Spørg os i #medlemsssystem_support på Slack hvis du mangler hjælp.",
                verbose_name="Overskriv DAWA",
            ),
        ),
    ]

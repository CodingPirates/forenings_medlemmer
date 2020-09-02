# Generated by Django 3.1 on 2020-09-02 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0023_address_dawa_overwrite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='dawa_overwrite',
            field=models.BooleanField(default=False, help_text='\n    Lader dig gemme en anden Længdegrad og breddegrad end den gemt i DAWA     (hvor vi henter adressedata).     Spørg os i #medlemsssystem_support på Slack hvis du mangler hjælp.\n    ', verbose_name='Overskriv DAWA'),
        ),
    ]

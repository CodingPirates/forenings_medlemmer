# Generated by Django 4.2.18 on 2025-04-13 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0072_alter_activity_price_in_dkk_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activity",
            name="member_justified",
            field=models.BooleanField(
                default=True,
                help_text="Bestemmer om personerne bliver til medlem i forhold til DUF.\n        De fleste aktiviteter er forløb/sæsoner og medlemsberettiget. Hvis\n        du er i tvivl, så spørg på Slack i #medlemssystem_support.",
                verbose_name="Aktiviteten gør personen til medlem",
            ),
        ),
        migrations.AlterField(
            model_name="activity",
            name="price_in_dkk",
            field=models.DecimalField(
                decimal_places=2,
                default=500,
                help_text="Hvis det er et forløb / en sæsonaktivitet fratrækkes der automatisk 150 kr. til Coding Pirates Denmark pr. barn.",
                max_digits=10,
                verbose_name="Pris",
            ),
        ),
        migrations.AlterField(
            model_name="activityinvite",
            name="price_in_dkk",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Hvis det er et forløb / en sæsonaktivitet fratrækkes der automatisk 150 kr. til Coding Pirates Denmark pr. deltager. Denne pris overskriver prisen på aktiviteten. Angiv kun en pris hvis denne deltager skal have en anden pris end angivet i aktiviteten. Hvis der angives en anden pris, skal noten udfyldes med en begrundelse for denne prisoverskrivelse. Denne note er synlig for den inviterede deltager.",
                max_digits=10,
                null=True,
                verbose_name="Pris",
            ),
        ),
    ]

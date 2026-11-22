from django.db import migrations, models
from django.db.models import F


def consent_to_consent_at(apps, schema_editor):
    VolunteerRequest = apps.get_model("members", "VolunteerRequest")
    VolunteerRequest.objects.filter(consent=True).update(consent_at=F("created"))


def consent_at_to_consent(apps, schema_editor):
    VolunteerRequest = apps.get_model("members", "VolunteerRequest")
    VolunteerRequest.objects.filter(consent_at__isnull=False).update(consent=True)


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0122_volunteer_confirmation_status_values"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteerrequest",
            name="consent_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Samtykke til opbevaring af oplysninger",
            ),
        ),
        migrations.RunPython(consent_to_consent_at, consent_at_to_consent),
        migrations.RemoveField(
            model_name="volunteerrequest",
            name="consent",
        ),
    ]

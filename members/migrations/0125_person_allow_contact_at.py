from django.db import migrations, models
from django.db.models import F

FIELDS = ("allow_contact_from_cpdk", "allow_contact_from_other")


def booleans_to_timestamps(apps, schema_editor):
    Person = apps.get_model("members", "Person")
    for field in FIELDS:
        Person.objects.filter(**{field: True}).update(**{f"{field}_at": F("added_at")})


def timestamps_to_booleans(apps, schema_editor):
    Person = apps.get_model("members", "Person")
    for field in FIELDS:
        Person.objects.filter(**{f"{field}_at__isnull": False}).update(**{field: True})


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0124_volunteerrequest_allow_contact_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="allow_contact_from_cpdk_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Må Coding Pirates Denmark kontakte mig?",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="allow_contact_from_other_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Må andre afdelinger kontakte mig?",
            ),
        ),
        migrations.RunPython(booleans_to_timestamps, timestamps_to_booleans),
        migrations.RemoveField(
            model_name="person",
            name="allow_contact_from_cpdk",
        ),
        migrations.RemoveField(
            model_name="person",
            name="allow_contact_from_other",
        ),
    ]

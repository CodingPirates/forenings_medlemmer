from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0088_person_allow_cpdk_contact"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteerrequest",
            name="allow_contact_from_cpdk",
            field=models.BooleanField(
                default=False,
                verbose_name="Må Coding Pirates Denmark kontakte mig?",
            ),
        ),
        migrations.AddField(
            model_name="volunteerrequest",
            name="allow_contact_from_other",
            field=models.BooleanField(
                default=False,
                verbose_name="Må andre afdelinger kontakte mig?",
            ),
        ),
    ]

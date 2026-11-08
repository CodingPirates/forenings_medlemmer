from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0112_merge_20260823_1337"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteerrequest",
            name="consent",
            field=models.BooleanField(
                default=False,
                verbose_name="Samtykke til opbevaring af oplysninger",
            ),
        ),
    ]

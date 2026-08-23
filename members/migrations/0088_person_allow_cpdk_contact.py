from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0087_merge_20260329_1335"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="allow_contact_from_cpdk",
            field=models.BooleanField(
                default=False,
                verbose_name="Må Coding Pirates Denmark kontakte mig?",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="allow_contact_from_other",
            field=models.BooleanField(
                default=False,
                verbose_name="Må andre afdelinger kontakte mig?",
            ),
        ),
    ]

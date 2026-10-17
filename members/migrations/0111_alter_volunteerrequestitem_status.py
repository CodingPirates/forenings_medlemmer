from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0110_merge_20260615_0811"),
    ]

    operations = [
        migrations.AlterField(
            model_name="volunteerrequestitem",
            name="status",
            field=models.CharField(
                choices=[
                    ("NEW", "Ny anmodning"),
                    ("REJECTED", "Afvist af afdeling"),
                    ("NOT_INTERESTED", "Person er ikke interesseret"),
                    ("WAITING", "Venter på at personen oprettes i systemet"),
                    ("ACTIVE", "Aktiv"),
                    ("CLOSED", "Afdeling er lukket"),
                ],
                default="NEW",
                max_length=20,
                verbose_name="Status",
            ),
        ),
    ]

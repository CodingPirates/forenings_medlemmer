from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0091_repair_contact_sharing_columns"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteer",
            name="user_confirmation_status",
            field=models.CharField(
                choices=[
                    ("APPROVED_BY_USER", "Godkendt af bruger"),
                    ("WAITING_FOR_USER", "Venter på bruger"),
                    ("REJECTED_BY_USER", "Afvist af bruger"),
                ],
                default="APPROVED_BY_USER",
                max_length=32,
                verbose_name="Brugerbekræftelse",
            ),
        ),
    ]

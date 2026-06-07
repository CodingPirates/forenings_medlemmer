from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0087_merge_20260329_1335"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteer",
            name="allow_cpdk_contact",
            field=models.BooleanField(
                default=False,
                verbose_name="Må Coding Pirates Denmark kontakte mig?",
            ),
        ),
    ]

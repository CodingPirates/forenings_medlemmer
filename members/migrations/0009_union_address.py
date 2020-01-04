# Generated by Django 2.2.8 on 2019-12-31 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0008_move_address_to_dep"),
    ]

    operations = [
        migrations.AddField(
            model_name="union",
            name="address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="members.Address",
            ),
        ),
    ]

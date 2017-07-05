from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0022_remove_department_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='max_participants',
            field=models.PositiveIntegerField(verbose_name='Max Holdstørrelse', default=30),
        ),
        migrations.AddField(
            model_name='activity',
            name='price',
            field=models.IntegerField(verbose_name='Pris (øre)', default=0),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='department',
            field=models.ForeignKey(default=0, to='members.Department'),
            preserve_default=False,
        ),
    ]

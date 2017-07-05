from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0024_auto_20150720_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='instructions',
            field=models.TextField(default='', verbose_name='Tilmeldings instruktioner'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='activity',
            name='description',
            field=models.TextField(verbose_name='Beskrivelse'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='open_hours',
            field=models.CharField(max_length=200, verbose_name='Tidspunkt'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='placename',
            field=models.CharField(max_length=200, verbose_name='Stednavn', blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='price',
            field=models.IntegerField(default=500, verbose_name='Pris (øre)'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='responsible_contact',
            field=models.EmailField(max_length=254, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='responsible_name',
            field=models.CharField(max_length=4, verbose_name='Afdelingsleder'),
        ),
    ]

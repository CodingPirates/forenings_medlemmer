from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0013_member_member_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='confirmed_dtm',
            field=models.DateTimeField(verbose_name='Bekræftet', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='family',
            name='deleted_dtm',
            field=models.DateTimeField(verbose_name='Slettet', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='family',
            name='last_visit_dtm',
            field=models.DateTimeField(verbose_name='Sidst besøgt', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='deleted_dtm',
            field=models.DateTimeField(verbose_name='Slettet', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='photo_permission',
            field=models.CharField(max_length=2, verbose_name='Foto tilladelse', default='ND', choices=[('OK', 'Tilladelse givet'), ('ND', 'Ikke taget stilling'), ('NO', 'Ikke tilladt')]),
        ),
    ]

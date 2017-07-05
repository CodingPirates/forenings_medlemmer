from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_auto_20150602_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailitem',
            name='family',
            field=models.ForeignKey(null=True, to='members.Family'),
        ),
        migrations.AddField(
            model_name='emailitem',
            name='reciever',
            field=models.EmailField(max_length=254, default='test@codingpirates.dk'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='template_help',
            field=models.TextField(verbose_name='Hjælp omkring template variable', blank=True),
        ),
        migrations.AlterField(
            model_name='emailitem',
            name='person',
            field=models.ForeignKey(null=True, to='members.Person'),
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='updated_dtm',
            field=models.DateTimeField(verbose_name='Sidst redigeret', auto_now_add=True),
        ),
    ]

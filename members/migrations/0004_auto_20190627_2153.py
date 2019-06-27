# Generated by Django 2.2.2 on 2019-06-27 19:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_auto_20190618_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='active_activities',
            field=models.IntegerField(verbose_name='Aktiviteter der er igang'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='activities',
            field=models.IntegerField(verbose_name='Aktiviteter i alt'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='activity_participants',
            field=models.IntegerField(verbose_name='Deltagere på aktiviteter over al tid'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='current_activity_participants',
            field=models.IntegerField(verbose_name='Deltagere på aktiviteter'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.Department'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='members',
            field=models.IntegerField(verbose_name='Medlemmer'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='payments',
            field=models.IntegerField(verbose_name='Betalinger'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='timestamp',
            field=models.DateTimeField(verbose_name='Kørsels tidspunkt'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='volunteers',
            field=models.IntegerField(verbose_name='Frivillige'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='volunteers_female',
            field=models.IntegerField(verbose_name='Frivillige Kvinder'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='volunteers_male',
            field=models.IntegerField(verbose_name='Frivillige Mænd'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='waitinglist',
            field=models.IntegerField(verbose_name='Venteliste'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsdepartment',
            name='waitingtime',
            field=models.DurationField(verbose_name='Ventetid'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsgeneral',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Kørsels tidspunkt'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsregion',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Kørsels tidspunkt'),
        ),
        migrations.AlterField(
            model_name='dailystatisticsunion',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Kørsels tidspunkt'),
        ),
    ]

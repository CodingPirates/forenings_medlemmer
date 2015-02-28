# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('description', models.CharField(max_length=10000, verbose_name='Beskrivelse')),
                ('start', models.DateField(verbose_name='Start')),
                ('end', models.DateField(verbose_name='Slut')),
            ],
            options={
                'verbose_name_plural': 'Aktiviteter',
                'verbose_name': 'aktivitet',
                'ordering': ['start'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('activity', models.ForeignKey(to='members.Activity')),
            ],
            options={
                'verbose_name_plural': 'Invitationer',
                'verbose_name': 'invitation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('activity', models.ForeignKey(to='members.Activity')),
            ],
            options={
                'verbose_name_plural': 'Deltagere',
                'verbose_name': 'deltager',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
            ],
            options={
                'verbose_name_plural': 'Afdelinger',
                'verbose_name': 'afdeling',
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('unique', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
                ('email', models.EmailField(unique=True, max_length=75)),
            ],
            options={
                'verbose_name_plural': 'Familier',
                'verbose_name': 'familie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktiv')),
                ('member_since', models.DateTimeField(verbose_name='Indmeldt', auto_now_add=True)),
                ('department', models.ForeignKey(to='members.Department')),
            ],
            options={
                'verbose_name_plural': 'Medlemmer',
                'verbose_name': 'medlem',
                'ordering': ['is_active', 'member_since'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('street', models.CharField(max_length=200, verbose_name='Adresse')),
                ('placename', models.CharField(max_length=200, verbose_name='Stednavn', blank=True)),
                ('zipcity', models.CharField(max_length=200, verbose_name='Postnr. og by')),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('phone', models.CharField(max_length=50, verbose_name='Telefon', blank=True)),
                ('has_certificate', models.DateField(verbose_name='Børneattest', blank=True, null=True)),
                ('on_waiting_list', models.BooleanField(default=False, verbose_name='Venteliste')),
                ('on_waiting_list_since', models.DateField(verbose_name='Tilføjet', auto_now_add=True)),
                ('membertype', models.CharField(default='PA', max_length=2, choices=[('PA', 'Forælder'), ('GU', 'Værge'), ('CH', 'Barn'), ('NA', 'Andet')])),
                ('family', models.ForeignKey(to='members.Family')),
            ],
            options={
                'verbose_name_plural': 'Personer',
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(to='members.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='member',
            name='person',
            field=models.ForeignKey(to='members.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activityparticipant',
            name='member',
            field=models.ForeignKey(to='members.Member'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activityinvite',
            name='person',
            field=models.ForeignKey(to='members.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='department',
            field=models.ForeignKey(to='members.Department'),
            preserve_default=True,
        ),
    ]

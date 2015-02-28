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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('description', models.CharField(max_length=10000, verbose_name='Beskrivelse')),
                ('start', models.DateField(verbose_name='Start')),
                ('end', models.DateField(verbose_name='Slut')),
            ],
            options={
                'verbose_name': 'aktivitet',
                'ordering': ['start'],
                'verbose_name_plural': 'Aktiviteter',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('unique', django_extensions.db.fields.UUIDField(blank=True, editable=False)),
                ('activity', models.ForeignKey(to='members.Activity')),
            ],
            options={
                'verbose_name': 'invitation',
                'verbose_name_plural': 'Invitationer',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('activity', models.ForeignKey(to='members.Activity')),
            ],
            options={
                'verbose_name': 'deltager',
                'verbose_name_plural': 'Deltagere',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
            ],
            options={
                'verbose_name': 'afdeling',
                'ordering': ['name'],
                'verbose_name_plural': 'Afdelinger',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('unique', django_extensions.db.fields.UUIDField(blank=True, editable=False)),
                ('email', models.EmailField(unique=True, max_length=75)),
            ],
            options={
                'verbose_name': 'familie',
                'verbose_name_plural': 'Familier',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('is_active', models.BooleanField(verbose_name='Aktiv', default=True)),
                ('member_since', models.DateTimeField(auto_now_add=True, verbose_name='Indmeldt')),
                ('department', models.ForeignKey(to='members.Department')),
            ],
            options={
                'verbose_name': 'medlem',
                'ordering': ['is_active', 'member_since'],
                'verbose_name_plural': 'Medlemmer',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('membertype', models.CharField(max_length=2, choices=[('PA', 'Forælder'), ('GU', 'Værge'), ('CH', 'Barn'), ('NA', 'Andet')], verbose_name='Type', default='PA')),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('street', models.CharField(max_length=200, verbose_name='Adresse')),
                ('placename', models.CharField(max_length=200, verbose_name='Stednavn', blank=True)),
                ('zipcity', models.CharField(max_length=200, verbose_name='Postnr. og by')),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('phone', models.CharField(max_length=50, verbose_name='Telefon', blank=True)),
                ('has_certificate', models.DateField(null=True, verbose_name='Børneattest', blank=True)),
                ('on_waiting_list', models.BooleanField(verbose_name='Venteliste', default=False)),
                ('on_waiting_list_since', models.DateField(auto_now_add=True, verbose_name='Tilføjet')),
                ('family', models.ForeignKey(to='members.Family')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Personer',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
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

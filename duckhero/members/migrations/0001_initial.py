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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
            name='Member',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktiv')),
                ('member_since', models.DateTimeField(verbose_name='Indmeldt', auto_now_add=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('street', models.CharField(max_length=200, verbose_name='Adresse')),
                ('placename', models.CharField(max_length=200, verbose_name='Stednavn')),
                ('zipcity', models.CharField(max_length=200, verbose_name='Postnr. og by')),
                ('email', models.EmailField(max_length=75)),
                ('unique', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('has_certificate', models.BooleanField(default=False, verbose_name='Børneattest')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(to='members.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WaitingList',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('added', models.DateTimeField(verbose_name='Tilføjet', auto_now_add=True)),
                ('department', models.ForeignKey(to='members.Department')),
                ('person', models.ForeignKey(to='members.Person')),
            ],
            options={
                'verbose_name': 'person på venteliste',
                'ordering': ['added'],
                'verbose_name_plural': 'Venteliste',
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

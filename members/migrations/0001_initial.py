# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Navn', max_length=200)),
                ('description', models.CharField(verbose_name='Beskrivelse', max_length=10000)),
                ('start_date', models.DateField(verbose_name='Start')),
                ('end_date', models.DateField(verbose_name='Slut')),
            ],
            options={
                'verbose_name': 'aktivitet',
                'verbose_name_plural': 'Aktiviteter',
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='ActivityInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('unique', django.db.models.fields.UUIDField(blank=True, editable=False)),
                ('activity', models.ForeignKey(to='members.Activity')),
            ],
            options={
                'verbose_name': 'invitation',
                'verbose_name_plural': 'Invitationer',
            },
        ),
        migrations.CreateModel(
            name='ActivityParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('activity', models.ForeignKey(to='members.Activity')),
            ],
            options={
                'verbose_name': 'deltager',
                'verbose_name_plural': 'Deltagere',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Navn', max_length=200)),
                ('has_waiting_list', models.BooleanField(verbose_name='Venteliste', default=False)),
            ],
            options={
                'verbose_name': 'afdeling',
                'verbose_name_plural': 'Afdelinger',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EmailItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_dtm', models.DateTimeField(verbose_name='Oprettet', auto_now_add=True)),
                ('subject', models.CharField(verbose_name='Emne', blank=True, max_length=200)),
                ('body', models.CharField(verbose_name='Indhold', blank=True, max_length=10000)),
                ('sent_dtm', models.DateTimeField(verbose_name='Sendt', blank=True, null=True)),
                ('send_error', models.CharField(verbose_name='Fejl i afsendelse', blank=True, editable=False, max_length=200)),
                ('activity', models.ForeignKey(to='members.Activity', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('unique', django.db.models.fields.UUIDField(blank=True, editable=False)),
                ('email', models.EmailField(unique=True, max_length=254)),
            ],
            options={
                'verbose_name': 'familie',
                'verbose_name_plural': 'Familier',
            },
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_dtm', models.DateTimeField(verbose_name='Oprettet', auto_now_add=True)),
                ('body', models.TextField(verbose_name='Indhold')),
                ('family', models.ForeignKey(to='members.Family')),
            ],
            options={
                'verbose_name': 'Journal',
                'verbose_name_plural': 'Journaler',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('is_active', models.BooleanField(verbose_name='Aktiv', default=True)),
                ('member_since', models.DateTimeField(verbose_name='Indmeldt', editable=False)),
                ('department', models.ForeignKey(to='members.Department')),
            ],
            options={
                'verbose_name': 'medlem',
                'verbose_name_plural': 'Medlemmer',
                'ordering': ['is_active', 'member_since'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('membertype', models.CharField(verbose_name='Type', default='PA', choices=[('PA', 'Forælder'), ('GU', 'Værge'), ('CH', 'Barn'), ('NA', 'Frivillig')], max_length=2)),
                ('name', models.CharField(verbose_name='Navn', max_length=200)),
                ('zipcode', models.CharField(verbose_name='Postnummer', max_length=4)),
                ('city', models.CharField(verbose_name='By', max_length=200)),
                ('streetname', models.CharField(verbose_name='Vejnavn', max_length=200)),
                ('housenumber', models.CharField(verbose_name='Husnummer', max_length=5)),
                ('floor', models.CharField(verbose_name='Etage', blank=True, max_length=3)),
                ('door', models.CharField(verbose_name='Dør', blank=True, max_length=5)),
                ('placename', models.CharField(verbose_name='Stednavn', blank=True, max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(verbose_name='Telefon', blank=True, max_length=50)),
                ('has_certificate', models.DateField(verbose_name='Børneattest', blank=True, null=True)),
                ('added', models.DateField(verbose_name='Tilføjet', auto_now_add=True)),
                ('on_waiting_list', models.BooleanField(verbose_name='Venteliste', default=False)),
                ('on_waiting_list_since', models.DateTimeField(verbose_name='Tilføjet', editable=False)),
                ('family', models.ForeignKey(to='members.Family')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Personer',
            },
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(to='members.Member')),
            ],
        ),
        migrations.CreateModel(
            name='WaitingList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('on_waiting_list_since', models.DateField(verbose_name='Tilføjet', blank=True, null=True)),
                ('department', models.ForeignKey(to='members.Department')),
                ('person', models.ForeignKey(to='members.Person')),
            ],
            options={
                'ordering': ['on_waiting_list_since'],
                'verbose_name_plural': 'På venteliste',
            },
        ),
        migrations.AddField(
            model_name='member',
            name='person',
            field=models.ForeignKey(to='members.Person'),
        ),
        migrations.AddField(
            model_name='journal',
            name='person',
            field=models.ForeignKey(to='members.Person', null=True),
        ),
        migrations.AddField(
            model_name='emailitem',
            name='person',
            field=models.ForeignKey(to='members.Person'),
        ),
        migrations.AddField(
            model_name='activityparticipant',
            name='member',
            field=models.ForeignKey(to='members.Member'),
        ),
        migrations.AddField(
            model_name='activityinvite',
            name='person',
            field=models.ForeignKey(to='members.Person'),
        ),
        migrations.AddField(
            model_name='activity',
            name='department',
            field=models.ForeignKey(to='members.Department'),
        ),
    ]

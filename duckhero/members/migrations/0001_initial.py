# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Navn', max_length=200)),
                ('description', models.CharField(verbose_name='Beskrivelse', max_length=10000)),
                ('start', models.DateTimeField(verbose_name='Start')),
                ('end', models.DateTimeField(verbose_name='Slut')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('activity', models.ForeignKey(to='members.Activity')),
            ],
            options={
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
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Navn', max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('is_active', models.BooleanField(verbose_name='Aktiv', default=True)),
                ('member_since', models.DateTimeField(verbose_name='Indmeldt', auto_now_add=True)),
                ('department', models.ForeignKey(to='members.Department')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Navn', max_length=200)),
                ('street', models.CharField(verbose_name='Adresse', max_length=200)),
                ('placename', models.CharField(verbose_name='Stednavn', max_length=200)),
                ('zipcity', models.CharField(verbose_name='Postnr. og by', max_length=200)),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('has_certificate', models.BooleanField(default=False)),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('added', models.DateTimeField(verbose_name='Tilføjet', auto_now_add=True)),
                ('department', models.ForeignKey(to='members.Department')),
                ('person', models.ForeignKey(to='members.Person')),
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

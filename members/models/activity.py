#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

class Activity(models.Model):
    class Meta:
        verbose_name='Aktivitet'
        verbose_name_plural = 'Aktiviteter'
        ordering = ['department__zipcode','start_date']
    department = models.ForeignKey('Department')
    name = models.CharField('Navn',max_length=200)
    open_hours = models.CharField('Tidspunkt',max_length=200)
    responsible_name = models.CharField('Ansvarlig',max_length=200)
    responsible_contact = models.EmailField('E-mail')
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    zipcode = models.CharField('Postnummer',max_length=4)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=200)
    floor = models.CharField('Etage',max_length=200, blank=True)
    door = models.CharField('Dør',max_length=200, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    description = models.TextField('Beskrivelse', blank=False)
    instructions = models.TextField('Tilmeldings instruktioner', blank=True)
    start_date = models.DateField('Start')
    end_date = models.DateField('Slut')
    signup_closing = models.DateField('Tilmelding lukker', null=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    open_invite = models.BooleanField('Fri tilmelding', default=False)
    price_in_dkk = models.DecimalField('Pris',max_digits=10, decimal_places=2, default=500)
    max_participants = models.PositiveIntegerField('Max deltagere', default=30)
    max_age = models.PositiveIntegerField('Maximum Alder', default=17)
    min_age = models.PositiveIntegerField('Minimum Alder', default=7)

    def is_historic(self):
        return self.end_date < timezone.now()
    is_historic.short_description = 'Historisk?'

    def __str__(self):
        return self.department.name + ", " + self.name

    def is_season(self):
        return (self.end_date - self.start_date).days > 30

    def seats_left(self):
        return self.max_participants - self.activityparticipant_set.count()

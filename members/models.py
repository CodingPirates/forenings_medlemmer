#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django_extensions.db.fields import UUIDField
import uuid
import datetime
# Create your models here.

class Family(models.Model):
    class Meta:
        verbose_name = 'familie'
        verbose_name_plural = 'Familier'
    unique = UUIDField()
    email = models.EmailField(unique=True)
    def save(self, *args, **kwargs):
        ''' On creation set UUID '''
        if not self.id:
            self.unique = uuid.uuid4()
        self.email = self.email.lower()
        return super(Family, self).save(*args, **kwargs)
    def get_abosolute_url(self):
        return reverse('family_form', kwargs={'pk':self.unique})
    def __str__(self):
        return self.email

class Person(models.Model):
    class Meta:
        verbose_name_plural='Personer'
        ordering=['name']
    PARENT = 'PA'
    GUARDIAN = 'GU'
    CHILD = 'CH'
    OTHER = 'NA'
    MEMBER_TYPE_CHOICES = (
        (PARENT,'Forælder'),
        (GUARDIAN, 'Værge'),
        (CHILD, 'Barn'),
        (OTHER, 'Frivillig')
    )
    membertype = models.CharField('Type',max_length=2,choices=MEMBER_TYPE_CHOICES,default=PARENT)
    name = models.CharField('Navn',max_length=200)
    zipcode = models.CharField('Postnummer',max_length=4)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=5)
    floor = models.CharField('Etage',max_length=3, blank=True)
    door = models.CharField('Dør',max_length=5, blank=True)
    def address(self):
        return '{} {}{}'.format(self.streetname,self.housenumber,', {}{}'.format(self.floor,self.door) if self.floor != '' or self.door != '' else '')
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    has_certificate = models.DateField('Børneattest',blank=True, null=True)
    family = models.ForeignKey(Family)
    added = models.DateField('Tilføjet',auto_now_add=True, blank=True, editable=False)
    on_waiting_list = models.BooleanField('Venteliste', default=False)
    on_waiting_list_since = models.DateTimeField('Tilføjet', blank=False, editable=False)
    @property
    def number_on_waiting_list(self):
        return Person.objects.filter(on_waiting_list_since__lt = self.on_waiting_list_since,on_waiting_list=True).count()+1 if self.on_waiting_list else ''
    def save(self, *args, **kwargs):
        ''' On creation set on_waiting_list '''
        if not self.id:
            self.on_waiting_list = self.membertype == Person.CHILD
        return super(Person, self).save(*args, **kwargs)
    def __str__(self):
        return self.name

class Department(models.Model):
    class Meta:
        verbose_name_plural='Afdelinger'
        verbose_name='afdeling'
        ordering=['name']
    name = models.CharField('Navn',max_length=200)
    has_waiting_list = models.BooleanField('Venteliste',default=False)
    def no_members(self):
        return self.member_set.count()
    no_members.short_description = 'Antal medlemmer'
    def __str__(self):
        return self.name

class WaitingList(models.Model):
    class Meta:
        verbose_name_plural='På venteliste'
        ordering=['on_waiting_list_since']
    person = models.ForeignKey(Person)
    department = models.ForeignKey(Department)
    on_waiting_list_since = models.DateField('Tilføjet', blank=True, null=True)
    def number_on_waiting_list(self):
        return WaitingList.objects.filter(department = self.department,on_waiting_list_since__lt = self.on_waiting_list_since).count()+1
    def save(self, *args,**kwargs):
        ''' On creation set on_waiting_list '''
        if not self.id:
            self.on_waiting_list_since = self.person.added

class Member(models.Model):
    class Meta:
        verbose_name = 'medlem'
        verbose_name_plural = 'Medlemmer'
        ordering = ['is_active','member_since']
    department = models.ForeignKey(Department)
    person = models.ForeignKey(Person)
    is_active = models.BooleanField('Aktiv',default=True)
    member_since = models.DateTimeField('Indmeldt', blank=False, editable=False)
    def name(self):
        return '{}'.format(self.person)
    name.short_description = 'Navn'
    def __str__(self):
        return '{}, {}'.format(self.person,self.department)

class Activity(models.Model):
    class Meta:
        verbose_name='aktivitet'
        verbose_name_plural = 'Aktiviteter'
        ordering =['start_date']
    department = models.ForeignKey(Department)
    name = models.CharField('Navn',max_length=200)
    description = models.CharField('Beskrivelse',max_length=10000)
    start_date = models.DateField('Start')
    end_date = models.DateField('Slut')
    def is_historic(self):
        return self.end_date < datetime.date.today()
    is_historic.short_description = 'Historisk?'
    def __str__(self):
        return self.name

class ActivityInvite(models.Model):
    class Meta:
        verbose_name='invitation'
        verbose_name_plural = 'Invitationer'
    activity = models.ForeignKey(Activity)
    person = models.ForeignKey(Person)
    unique = UUIDField()
    def save(self, *args, **kwargs):
        ''' On creation set UUID '''
        if not self.id:
            self.unique = uuid.uuid4()
            super(ActivityInvite, self).save(*args, **kwargs)
            invite = EmailItem()
            invite.activity = self.activity
            invite.person = self.person
            invite.subject = 'Du er blevet inviteret til aktiviteten: {}'.format(self.activity.name)
            invite.body = self.activity.description
            return invite.save()
        return super(ActivityInvite, self).save(*args, **kwargs)
    def __str__(self):
        return '{}, {}'.format(self.activity,self.person)

class ActivityParticipant(models.Model):
    class Meta:
        verbose_name = 'deltager'
        verbose_name_plural = 'Deltagere'
    activity = models.ForeignKey(Activity)
    member = models.ForeignKey(Member)
    def __str__(self):
        return self.member.__str__()

class Volunteer(models.Model):
    member = models.ForeignKey(Member)
    def has_certificate(self):
        return self.person.has_certificate
    added = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    def __str__(self):
        return self.member.__str__()

class EmailItem(models.Model):
    person = models.ForeignKey(Person)
    activity = models.ForeignKey(Activity, null=True)
    created_dtm = models.DateTimeField('Oprettet',auto_now_add=True)
    subject = models.CharField('Emne',max_length=200, blank=True)
    body = models.CharField('Indhold', max_length=10000, blank=True)
    sent_dtm = models.DateTimeField('Sendt', blank=True, null=True)
    send_error = models.CharField('Fejl i afsendelse',max_length=200,blank=True, editable=False)

class Journal(models.Model):
    class Meta:
        verbose_name = 'Journal'
        verbose_name_plural = 'Journaler'
    family = models.ForeignKey(Family)
    person = models.ForeignKey(Person, null=True)
    created_dtm = models.DateTimeField('Oprettet',auto_now_add=True)
    body = models.TextField('Indhold')
    def __str__(self):
        return self.family.email
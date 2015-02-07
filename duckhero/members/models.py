from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField('Navn',max_length=200)
    street = models.CharField('Adresse',max_length=200)
    placename = models.CharField('Stednavn',max_length=200)
    zipcity = models.CharField('Postnr. og by',max_length=200)
    email = models.EmailField()

class Department(models.Model):
    name = models.CharField('Navn',max_length=200)

class WaitingList(models.Model):
    department = models.ForeignKey('Afdeling',Department)
    person = models.ForeignKey(Person)
    added = models.DateTimeField('Tilføjet',auto_now_add=True, blank=True)

class Member(models.Model):
    department = models.ForeignKey('Afdeling',Department)
    person = models.ForeignKey(Person)
    is_active = models.BooleanField('Aktiv',default=True)
    member_since = models.DateTimeField('Indmeldt',auto_now_add=True, blank=True)

class Activity(models.Model):
    department = models.ForeignKey('Afdeling',Department)
    name = models.CharField('Navn',max_length=200)
    description = models.CharField('description',max_length=10000)
    start = models.DateTimeField('Start')
    end = models.DateTimeField('Slut')

class ActivityInvite(models.Model):
    activity = models.ForeignKey('Aktivitet',Activity)
    person = models.ForeignKey(Person)

class ActivityParticipant(models.Model):
    activity = models.ForeignKey('Aktivitet',Activity)
    member = models.ForeignKey('Medlem',Member)

class Volunteer(models.Model):
    member = models.ForeignKey('Medlem',Member)
    department = models.ForeignKey('Afdeling',Department)
    has_certificate = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True, blank=True)

from django.db import models
import datetime
# Create your models here.
class Person(models.Model):
    name = models.CharField('Navn',max_length=200)
    street = models.CharField('Adresse',max_length=200)
    placename = models.CharField('Stednavn',max_length=200)
    zipcity = models.CharField('Postnr. og by',max_length=200)
    email = models.EmailField()
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField('Navn',max_length=200)
    def no_members(self):
        return self.member_set.count()
    no_members.short_description = "Antal medlemmer"
    def __str__(self):
        return self.name

class WaitingList(models.Model):
    department = models.ForeignKey(Department)
    person = models.ForeignKey(Person)
    added = models.DateTimeField('Tilføjet',auto_now_add=True, blank=True)
    def __str__(self):
        return '{}, {}'.format(self.department,self.person)

class Member(models.Model):
    department = models.ForeignKey(Department)
    person = models.ForeignKey(Person)
    is_active = models.BooleanField('Aktiv',default=True)
    member_since = models.DateTimeField('Indmeldt',auto_now_add=True, blank=True)
    def name(self):
        return '{}'.format(self.person)
    def __str__(self):
        return '{}, {}'.format(self.person,self.department)

class Activity(models.Model):
    department = models.ForeignKey(Department)
    name = models.CharField('Navn',max_length=200)
    description = models.CharField('Beskrivelse',max_length=10000)
    start = models.DateField('Start')
    end = models.DateField('Slut')
    def is_historic(self):
        return self.end < datetime.date.today()
    def __str__(self):
        return self.name

class ActivityInvite(models.Model):
    activity = models.ForeignKey(Activity)
    person = models.ForeignKey(Person)
    def __str__(self):
        return '{}, {}'.format(self.activity,self.person)

class ActivityParticipant(models.Model):
    activity = models.ForeignKey(Activity)
    member = models.ForeignKey(Member)
    def __str__(self):
        return self.member.__str__()

class Volunteer(models.Model):
    member = models.ForeignKey(Member)
    has_certificate = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True, blank=True)
    def __str__(self):
        return self.member.__str__()

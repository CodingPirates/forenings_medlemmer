from django.db import models
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
        return super(Family, self).save(*args, **kwargs)
    def __str__(self):
        return self.email

class Person(models.Model):
    class Meta:
        verbose_name_plural='Personer'
        ordering=['name']
    name = models.CharField('Navn',max_length=200)
    street = models.CharField('Adresse',max_length=200)
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    zipcity = models.CharField('Postnr. og by',max_length=200)
    email = models.EmailField(blank=True)
    has_certificate = models.DateField('Børneattest',blank=True, null=True)
    def unique(self):
        return self.family.unique if self.family != None else ''
    family = models.ForeignKey(Family)
    PARENT = 'PA'
    GUARDIAN = 'GU'
    CHILD = 'CH'
    OTHER = 'NA'
    MEMBER_TYPE_CHOICES = (
        (PARENT,'Forælder'),
        (GUARDIAN, 'Værge'),
        (CHILD, 'Barn'),
        (OTHER, 'Andet')
    )
    membertype = models.CharField(max_length=2,choices=MEMBER_TYPE_CHOICES,default=PARENT)
    def __str__(self):
        return self.name

class Department(models.Model):
    class Meta:
        verbose_name_plural='Afdelinger'
        verbose_name='afdeling'
        ordering=['name']
    name = models.CharField('Navn',max_length=200)
    def no_members(self):
        return self.member_set.count()
    no_members.short_description = 'Antal medlemmer'
    def __str__(self):
        return self.name

class WaitingList(models.Model):
    class Meta:
        verbose_name='person på venteliste'
        verbose_name_plural = 'Venteliste'
        ordering=['added']
    department = models.ForeignKey(Department)
    person = models.ForeignKey(Person)
    added = models.DateTimeField('Tilføjet',auto_now_add=True, blank=True, editable=False)
    def __str__(self):
        return '{}, {}'.format(self.department,self.person)

class Member(models.Model):
    class Meta:
        verbose_name = 'medlem'
        verbose_name_plural = 'Medlemmer'
        ordering = ['is_active','member_since']
    department = models.ForeignKey(Department)
    person = models.ForeignKey(Person)
    is_active = models.BooleanField('Aktiv',default=True)
    member_since = models.DateTimeField('Indmeldt',auto_now_add=True, blank=True, editable=False)
    def name(self):
        return '{}'.format(self.person)
    name.short_description = 'Navn'
    def __str__(self):
        return '{}, {}'.format(self.person,self.department)

class Activity(models.Model):
    class Meta:
        verbose_name='aktivitet'
        verbose_name_plural = 'Aktiviteter'
        ordering =['start']
    department = models.ForeignKey(Department)
    name = models.CharField('Navn',max_length=200)
    description = models.CharField('Beskrivelse',max_length=10000)
    start = models.DateField('Start')
    end = models.DateField('Slut')
    def is_historic(self):
        return self.end < datetime.date.today()
    is_historic.short_description = 'Historisk?'
    def __str__(self):
        return self.name

class ActivityInvite(models.Model):
    class Meta:
        verbose_name='invitation'
        verbose_name_plural = 'Invitationer'
    activity = models.ForeignKey(Activity)
    person = models.ForeignKey(Person)
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

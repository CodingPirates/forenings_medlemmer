#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django_extensions.db.fields import UUIDField
import uuid
import datetime
from pytz import timezone
from django.template import Engine, Context
from django.core.mail import send_mail
from django.utils import timezone as django_timezone

# Create your models here.

class Family(models.Model):
    class Meta:
        verbose_name = 'familie'
        verbose_name_plural = 'Familier'
    unique = UUIDField()
    email = models.EmailField(unique=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    confirmed_dtm = models.DateTimeField('Bekræftet', null=True, blank=True)
    last_visit_dtm = models.DateTimeField('Sidst besøgt', null=True, blank=True)
    deleted_dtm = models.DateTimeField('Slettet', null=True, blank=True)
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
    PHOTO_OK = 'OK'
    PHOTO_ND = 'ND'
    PHOTO_NOTOK = 'NO'
    PHOTO_PERMISSION_CHOICES = (
        (PHOTO_OK, 'Tilladelse givet'),
        (PHOTO_ND, 'Ikke taget stilling'),
        (PHOTO_NOTOK, 'Ikke tilladt'),
    )
    membertype = models.CharField('Type',max_length=2,choices=MEMBER_TYPE_CHOICES,default=PARENT)
    name = models.CharField('Navn',max_length=200)
    zipcode = models.CharField('Postnummer',max_length=4)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=5)
    floor = models.CharField('Etage',max_length=3, blank=True)
    door = models.CharField('Dør',max_length=5, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    def address(self):
        return '{} {}{}'.format(self.streetname,self.housenumber,', {}{}'.format(self.floor,self.door) if self.floor != '' or self.door != '' else '')
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    birthday = models.DateField('Fødselsdag', blank=True, null=True)
    has_certificate = models.DateField('Børneattest',blank=True, null=True)
    family = models.ForeignKey(Family)
    photo_permission = models.CharField('Foto tilladelse', max_length=2, choices=PHOTO_PERMISSION_CHOICES, default=PHOTO_ND)
    added = models.DateField('Tilføjet', default=django_timezone.now, blank=False)
    deleted_dtm = models.DateTimeField('Slettet', null=True, blank=True)
    def __str__(self):
        return self.name

class Department(models.Model):
    class Meta:
        verbose_name_plural='Afdelinger'
        verbose_name='afdeling'
        ordering=['name']
    name = models.CharField('Navn',max_length=200)
    description = models.TextField('Beskrivelse af afdeling', blank=True)
    open_hours = models.CharField('Åbningstid',max_length=4, blank=True)
    responsible_name = models.CharField('Afdelingsleder',max_length=4, blank=True)
    responsible_contact = models.EmailField('E-mail', blank=True)
    placename = models.CharField('Stednavn',max_length=4, blank=True)
    zipcode = models.CharField('Postnummer',max_length=4)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=5)
    floor = models.CharField('Etage',max_length=3, blank=True)
    door = models.CharField('Dør',max_length=5, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    has_waiting_list = models.BooleanField('Venteliste',default=False)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
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
        return super(WaitingList, self).save(*args, **kwargs)

class Member(models.Model):
    class Meta:
        verbose_name = 'medlem'
        verbose_name_plural = 'Medlemmer'
        ordering = ['is_active','member_since']
    department = models.ForeignKey(Department)
    person = models.ForeignKey(Person)
    is_active = models.BooleanField('Aktiv',default=True)
    member_since = models.DateTimeField('Indmeldt', blank=False, default=django_timezone.now)
    member_until = models.DateTimeField('Udmeldt', blank=True, default=None, null=True)
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
    open_hours = models.CharField('Tidspunkt',max_length=4, blank=True)
    responsible_name = models.CharField('Afdelingsleder',max_length=4, blank=True)
    responsible_contact = models.EmailField('E-mail', blank=True)
    placename = models.CharField('Stednavn',max_length=4)
    zipcode = models.CharField('Postnummer',max_length=4)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=5)
    floor = models.CharField('Etage',max_length=3, blank=True)
    door = models.CharField('Dør',max_length=5, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    description = models.CharField('Beskrivelse',max_length=10000)
    start_date = models.DateField('Start')
    end_date = models.DateField('Slut')
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    open_invite = models.BooleanField('Fri tilmelding', default=False)
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
    note = models.TextField('Besked / Note til arrangement', blank=True)
    def __str__(self):
        return self.member.__str__()

class Volunteer(models.Model):
    member = models.ForeignKey(Member)
    def has_certificate(self):
        return self.person.has_certificate
    added = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    def __str__(self):
        return self.member.__str__()

class EmailTemplate(models.Model):
    class Meta:
        verbose_name = 'Email Skabelon'
        verbose_name_plural = 'Email Skabeloner'
    idname = models.SlugField('Unikt reference navn',max_length=50, blank=False, unique=True)
    updated_dtm = models.DateTimeField('Sidst redigeret', auto_now=True)
    name = models.CharField('Skabelon navn',max_length=200, blank=False)
    description = models.CharField('Skabelon beskrivelse',max_length=200, blank=False)
    template_help = models.TextField('Hjælp omkring template variable', blank=True)
    from_address = models.EmailField();
    subject = models.CharField('Emne',max_length=200, blank=False)
    body_html = models.TextField('HTML Indhold', blank=True)
    body_text = models.TextField('Text Indhold', blank=True)
    def __str__(self):
        return self.name + " (ID:" + self.idname + ")"

    # Will create and put an email in Queue from this template.
    # It will try to to put usefull details in context, which in many cases can just be {}

    # context is always filled with:
    #  email, site

    # If possible it will also be filled with:
    #  person, family

    # recievers is expected to be a list of Person, Family or strings (email adresses)

    def makeEmail(self, recievers, context):

        if(type(recievers) is not list):
            recievers = [recievers]

        for reciever in recievers:
            # each reciever must be Person, Family or string (email)
            if type(reciever) not in (Person, Family, str):
                raise Exception("Reciever must be of type Person, Family or string")

            # figure out reciever
            if(type(reciever) is str):
                destination_address = reciever;
            elif(type(reciever) is Person):
                context['family'] = reciever
                destination_address = reciever.email;
            elif(type(reciever) is Family):
                context['family'] = reciever
                destination_address = reciever.email;

            # figure out Person and Family is applicable
            if(type(reciever) is Person):
                person = reciever
            elif('person' in context):
                person = context['person']
            else:
                person=None

            # figure out family
            if(type(reciever) is Family):
                family = reciever
            elif(type(reciever) is Person):
                family = reciever.family
            elif('family' in context):
                family = context['family']
            else:
                family=None

            # figure out activity
            if 'activity' in context:
                activity = context['activity']
            else:
                activity = None

            # department
            if 'department' in context:
                department = context['department']
            else:
                department = None

            # fill out known usefull stuff for context
            if 'email' not in context: context['email'] = destination_address
            if 'site' not in context: context['site'] = settings.BASE_URL
            if 'person' not in context: context['person'] = person
            if 'family' not in context: context['family'] = family

            # Make real context from dict
            context = Context(context)

            # render the template
            html_template = Engine.get_default().from_string(self.body_html)
            text_template = Engine.get_default().from_string(self.body_text)
            subject_template = Engine.get_default().from_string(self.subject)

            html_content = html_template.render(context)
            text_content = text_template.render(context)
            subject_content = subject_template.render(context)

            email = EmailItem.objects.create(template = self,
                reciever = destination_address,
                person=person,
                family=family,
                activity=activity,
                department = department,
                subject = subject_content,
                body_html = html_content,
                body_text = text_content)
            email.save()
            return email


class EmailItem(models.Model):
    person = models.ForeignKey(Person, null=True)
    family = models.ForeignKey(Family, null=True)
    reciever = models.EmailField(null=False)
    template = models.ForeignKey(EmailTemplate, null=True)
    bounce_token = UUIDField(default=uuid.uuid4, null=False)
    activity = models.ForeignKey(Activity, null=True)
    department = models.ForeignKey(Department, null=True)
    created_dtm = models.DateTimeField('Oprettet',auto_now_add=True)
    subject = models.CharField('Emne',max_length=200, blank=True)
    body_html = models.TextField('HTML Indhold', blank=True)
    body_text = models.TextField('Text Indhold', blank=True)
    sent_dtm = models.DateTimeField('Sendt tidstempel', blank=True, null=True)
    send_error = models.CharField('Fejl i afsendelse',max_length=200,blank=True, editable=False)

    # send this email. Notice no checking of race condition, so this should be called by
    # cronscript and made sure the same mail is not sent multiple times in parallel
    def send(self):
        if settings.DEBUG:
            # never use actual destination in debug
            destination_email = settings.DEBUG_EMAIL_DESTINATION
        else:
            destination_email = self.reciever

        self.sent_dtm = datetime.datetime.now(timezone('Europe/Copenhagen'))
        try:
            send_mail(self.subject, self.body_text, settings.SITE_CONTACT, (destination_email,), html_message=self.body_html)
        except Exception as e:
            self.send_error = str(type(e))
            self.send_error = self.send_error + str(e)
            self.save()
            raise e # forward exception to job control

        self.save()

class Notification(models.Model):
    family = models.ForeignKey(Family)
    email = models.ForeignKey(EmailItem)
    update_info_dtm = models.DateTimeField('Bedt om opdatering af info', blank=True, null=True)
    warned_deletion_info_dtm = models.DateTimeField('Advaret om sletning fra liste', blank=True, null=True)
    anounced_department = models.ForeignKey(Department, null=True)
    anounced_activity = models.ForeignKey(Activity, null=True)

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

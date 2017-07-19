#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.fields import UUIDField
import uuid
from datetime import datetime, timedelta
from django.template import Engine, Context
from django.core.mail import send_mail
from django.utils import timezone, html
from django.contrib.auth.models import User
from quickpay_api_client import QPClient
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import requests, json


def format_address(streetname, housenumber, floor=None, door=None):
    address = streetname + " " + housenumber
    if(floor != '' and door != ''):
        address = address + ", " + floor + ". " + door + "."

    if(floor != '' and door == ''):
        address = address + ", " + floor + "."

    if(floor == '' and door != ''):
        address = address + ", " + door + "."

    return address

# Create your models here.

class Family(models.Model):
    class Meta:
        verbose_name = 'Familie'
        verbose_name_plural = 'Familier'
        permissions = (
            ("view_family_unique", "Can view family UUID field (password) - gives access to address"),
        )

    unique = UUIDField()
    email = models.EmailField(unique=True)
    dont_send_mails = models.BooleanField('Vil ikke kontaktes', default=False)
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
    def send_link_email(self,):
        EmailTemplate.objects.get(idname = 'LINK').makeEmail(self, {})
    def get_first_parent(self):
        try:
            parent = self.person_set.filter(membertype__in=(Person.PARENT, Person.GUARDIAN))[0]
        except IndexError:
            return None
        return parent

class Person(models.Model):
    class Meta:
        verbose_name = "Person"
        verbose_name_plural='Personer'
        ordering=['added']
        permissions = (
            ("view_full_address", "Can view persons full address + phonenumber + email"),
            ("view_all_persons", "Can view persons not related to department"),
        )

    PARENT = 'PA'
    GUARDIAN = 'GU'
    CHILD = 'CH'
    OTHER = 'NA'
    MEMBER_TYPE_CHOICES = (
        (PARENT,'Forælder'),
        (GUARDIAN, 'Værge'),
        (CHILD, 'Barn'),
        (OTHER, 'Anden')
    )
    MALE = 'MA'
    FEMALE = 'FM'
    MEMBER_GENDER_CHOICES = (
        (MALE, 'Dreng'),
        (FEMALE, 'Pige')
        )
    MEMBER_ADULT_GENDER_CHOICES = (
        (MALE, 'Mand'),
        (FEMALE, 'Kvinde')
        )
    membertype = models.CharField('Type',max_length=2,choices=MEMBER_TYPE_CHOICES,default=PARENT)
    name = models.CharField('Navn',max_length=200)
    zipcode = models.CharField('Postnummer',max_length=4, blank=True)
    city = models.CharField('By', max_length=200, blank=True)
    streetname = models.CharField('Vejnavn',max_length=200, blank=True)
    housenumber = models.CharField('Husnummer',max_length=5, blank=True)
    floor = models.CharField('Etage',max_length=3, blank=True)
    door = models.CharField('Dør',max_length=5, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    gender = models.CharField('Køn',max_length=20,choices=MEMBER_GENDER_CHOICES,default=None, null=True)
    birthday = models.DateField('Fødselsdag', blank=True, null=True)
    has_certificate = models.DateField('Børneattest',blank=True, null=True)
    family = models.ForeignKey(Family)
    notes = models.TextField('Noter', blank=True, null=False, default ="")
    added = models.DateTimeField('Tilføjet', default=timezone.now, blank=False)
    deleted_dtm = models.DateTimeField('Slettet', null=True, blank=True)
    def __str__(self):
        return self.name

    def address(self):
        return format_address(self.streetname, self.housenumber, self.floor, self.door)

    def age_from_birthdate(self, date):
        today = timezone.now().date()
        return today.year - date.year - ((today.month, today.day) < (date.month, date.day))

    def age_years(self):
        if(self.birthday != None):
            return self.age_from_birthdate(self.birthday)
        else:
            return 0
    age_years.admin_order_field = '-birthday'
    age_years.short_description = 'Alder'

    def firstname(self):
        return self.name.partition(' ')[0]
    firstname.admin_order_field = 'name'
    firstname.short_description = 'Fornavn'

class Union(models.Model):
    class Meta:
        verbose_name_plural='Foreninger'
        verbose_name='Forening'
        ordering=['name']
    name = models.CharField('Foreningens navn',max_length=200)
    chairman = models.CharField('Formand',max_length=200, blank=True)
    chairman_email = models.EmailField('Formandens email', blank=True)
    second_chair = models.CharField('Næstformand',max_length=200, blank=True)
    second_chair_email = models.EmailField('Næstformandens email', blank=True)
    cashier = models.CharField('Kasserer', max_length=200, blank=True)
    cashier_email = models.EmailField('Kassererens email', blank=True)
    secretary = models.CharField('Sekretær', max_length=200, blank=True)
    secratary_email = models.EmailField('Sekretærens email', blank=True)
    union_email = models.EmailField('Foreningens email', blank=True)
    statues = models.URLField('Link til gældende vedtægter', blank=True)
    founded = models.DateField('Stiftet', blank=True, null=True)
    regions = (
        ('S' , 'Sjælland'),
        ('J' , 'Jylland'),
        ('F' , 'Fyn'),
        ('Ø' , 'Øer')
    )
    region = models.CharField('region', max_length=1, choices=regions)

    placename = models.CharField('Stednavn',max_length=200, blank=True)
    zipcode = models.CharField('Postnummer',max_length=10)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=10)
    floor = models.CharField('Etage',max_length=10, blank=True)
    door = models.CharField('Dør',max_length=10, blank=True)
    boardMembers = models.TextField('Menige medlemmer', blank=True)
    bank_main_org = models.BooleanField('Sæt kryds hvis I har konto hos hovedforeningen (og ikke har egen bankkonto).',default=True)
    bank_account = models.CharField('Bankkonto:',max_length=15,blank=True,help_text='Kontonummer i formatet 1234-1234567890',validators=[RegexValidator(regex="^[0-9]{4} *?-? *?[0-9]{6,10} *?$",message="Indtast kontonummer i det rigtige format.")])
    def __str__(self):
        return "Foreningen for " + self.name

    def clean(self):
        if(self.bank_main_org==False and not self.bank_account):
            raise ValidationError('Vælg om foreningen har konto hos hovedforeningen. Hvis ikke skal bankkonto udfyldes.')

class Department(models.Model):
    class Meta:
        verbose_name_plural='Afdelinger'
        verbose_name='Afdeling'
        ordering=['zipcode']
    name = models.CharField('Navn',max_length=200)
    description = models.TextField('Beskrivelse af afdeling', blank=True)
    open_hours = models.CharField('Åbningstid',max_length=200, blank=True)
    responsible_name = models.CharField('Afdelingsleder',max_length=200, blank=True)
    responsible_contact = models.EmailField('E-mail', blank=True)
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    zipcode = models.CharField('Postnummer',max_length=10)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=10)
    floor = models.CharField('Etage',max_length=10, blank=True)
    door = models.CharField('Dør',max_length=10, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    has_waiting_list = models.BooleanField('Venteliste',default=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    created = models.DateField('Oprettet', blank=False, default=timezone.now)
    closed_dtm = models.DateField('Lukket', blank=True, null=True, default=None)
    isVisible  = models.BooleanField('Kan ses på afdelingssiden', default=True)
    isOpening  = models.BooleanField('Er afdelingen under opstart', default=False)
    website    = models.URLField('Hjemmeside', blank=True)
    union      = models.ForeignKey(Union, verbose_name="Lokalforening", blank=False, null=False)
    longtitude = models.DecimalField("Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6)
    latitude   = models.DecimalField("Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6)
    onMap      = models.BooleanField("Skal den være på kortet?", default=True)

    def no_members(self):
        return self.member_set.count()
    no_members.short_description = 'Antal medlemmer'
    def __str__(self):
        return self.name
    def address(self):
        return format_address(self.streetname, self.housenumber, self.floor, self.door)
    def addressWithZip(self):
        return self.address() + ", " + self.zipcode + " " + self.city
    def toHTML(self):
        myHTML = ''
        if(self.website == ''):
            myHTML += '<strong>Coding Pirates ' + html.escape(self.name) + '</strong><br>'
        else:
            myHTML += '<a href="' + html.escape(self.website) + '">' + \
            '<strong>Coding Pirates ' + html.escape(self.name) + '</strong></a><br>'
        if self.isOpening:
            myHTML += "<strong>Afdelingen slår snart dørene op!</strong><br>"
        if self.placename != '':
            myHTML += html.escape(self.placename) + '<br>'
        myHTML += html.escape(self.address()) + '<br>' + html.escape(self.zipcode) + ", " + html.escape(self.city) + '<br>'
        myHTML += 'Afdelingsleder: ' + html.escape(self.responsible_name) + '<br>'
        myHTML += 'E-mail: <a href="mailto:' +html.escape(self.responsible_contact) + '">'+ html.escape(self.responsible_contact) + '</a><br>'
        myHTML +=  'Tidspunkt: ' + html.escape(self.open_hours)
        return myHTML
    def getLongLat(self):
        if (self.latitude == None or self.longtitude == None):
            addressID = 0
            dist = 0
            req = 'https://dawa.aws.dk/datavask/adresser?betegnelse=' + self.addressWithZip().replace(" ", "%20")
            try:
                washed = json.loads(requests.get(req).text)
                addressID = washed['resultater'][0]['adresse']['id']
                dist = washed['resultater'][0]['vaskeresultat']['afstand']
            except Exception as error:
                print("Couldn't find addressID for " + self.name)
                print("Error " +  str(error))
            if (addressID != 0 and dist < 10):
                try:
                    req = 'https://dawa.aws.dk/adresser/' + addressID + "?format=geojson"
                    address = json.loads(requests.get(req).text)
                    self.latitude   =  address['geometry']['coordinates'][0]
                    self.longtitude =  address['geometry']['coordinates'][1]
                    self.save()
                    print("Opdateret for " + self.name)
                    print("Updated coordinates for " + self.name)
                    return(self.latitude, self.longtitude)
                except Exception as error:
                    print("Couldn't find coordinates for " + self.name)
                    print("Error " +  str(error))
        else:
            return(self.latitude, self.longtitude)

    def new_volunteer_email(self,volunteer_name):
        # First fetch department leaders email
        new_vol_email = EmailTemplate.objects.get(idname = 'VOL_NEW')
        context = {
            'department': self,
            'volunteer_name': volunteer_name,
        }
        new_vol_email.makeEmail(self, context)

class WaitingList(models.Model):
    class Meta:
        verbose_name="På venteliste"
        verbose_name_plural='På ventelister'
        ordering=['on_waiting_list_since']
    person = models.ForeignKey(Person)
    department = models.ForeignKey(Department)
    on_waiting_list_since = models.DateField('Venteliste position', blank=False, null=False)
    added_dtm = models.DateField('Tilføjet', blank=False, null=False, default=timezone.now)
    def number_on_waiting_list(self):
        return WaitingList.objects.filter(department = self.department, on_waiting_list_since__lt = self.on_waiting_list_since).count()+1
    number_on_waiting_list.short_description = 'Position på venteliste'
    def save(self, *args,**kwargs):
        ''' On creation set on_waiting_list '''
        if not self.id:
            self.on_waiting_list_since = self.person.added
        return super(WaitingList, self).save(*args, **kwargs)

class Member(models.Model):
    class Meta:
        verbose_name = 'Medlem'
        verbose_name_plural = 'Medlemmer'
        ordering = ['is_active','member_since']
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    person = models.OneToOneField(Person, on_delete=models.PROTECT)
    is_active = models.BooleanField('Aktiv',default=True)
    member_since = models.DateField('Indmeldt', blank=False, default=timezone.now)
    member_until = models.DateField('Udmeldt', blank=True, default=None, null=True)
    def name(self):
        return '{}'.format(self.person)
    name.short_description = 'Navn'
    def __str__(self):
        return '{}, {}'.format(self.person,self.department)

class Activity(models.Model):
    class Meta:
        verbose_name='Aktivitet'
        verbose_name_plural = 'Aktiviteter'
        ordering = ['department__zipcode','start_date']
    department = models.ForeignKey(Department)
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
        return self.end_date < datetime.date.today()
    is_historic.short_description = 'Historisk?'
    def __str__(self):
        return self.department.name + ", " + self.name
    def is_season(self):
        return (self.end_date - self.start_date).days > 30
    def seats_left(self):
        return self.max_participants - self.activityparticipant_set.count()

# Calculate a day 3 months in future
def defaultInviteExpiretime():
    now = timezone.now()
    return now + timedelta(days=30*3)
class ActivityInvite(models.Model):
    class Meta:
        verbose_name='Invitation'
        verbose_name_plural = 'Invitationer'
        unique_together = ('activity', 'person')
    activity = models.ForeignKey(Activity)
    person = models.ForeignKey(Person)
    invite_dtm = models.DateField('Inviteret', default=timezone.now)
    expire_dtm = models.DateField('Udløber', default=defaultInviteExpiretime)
    rejected_dtm = models.DateField('Afslået', blank=True, null=True)

    def clean(self):
        # Make sure we are not inviting outside activivty age limit
        if(self.person.age_years() < self.activity.min_age or self.person.age_years() > self.activity.max_age):
            raise ValidationError('Aktiviteten er kun for personer mellem ' + str(self.activity.min_age) + ' og ' + str(self.activity.max_age) + ' år');

    def save(self, *args, **kwargs):
        if not self.id:
            super(ActivityInvite, self).save(*args, **kwargs)
            template = EmailTemplate.objects.get(idname='ACT_INVITE')
            context={'activity': self.activity,
                     'activity_invite' : self,
                     'person' : self.person,
                     'family' : self.person.family,
                     }
            if self.person.email and (self.person.email != self.person.family.email):
                # If invited has own email, also send to that.
                template.makeEmail([self.person, self.person.family], context)
            else:
                #otherwise use only family
                template.makeEmail(self.person.family, context)
            # remove from department waiting list
            if self.activity.is_season():
                WaitingList.objects.filter(person=self.person, department=self.activity.department).delete()
        return super(ActivityInvite, self).save(*args, **kwargs)
    def __str__(self):
        return '{}, {}'.format(self.activity,self.person)

class ActivityParticipant(models.Model):
    class Meta:
        verbose_name = 'Deltager'
        verbose_name_plural = 'Deltagere'
        unique_together = ('activity', 'member')
    added_dtm = models.DateField('Tilmeldt', default=timezone.now)
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    member = models.ForeignKey(Member)
    note = models.TextField('Besked / Note til arrangement', blank=True)
    PHOTO_OK = 'OK'
    PHOTO_NOTOK = 'NO'
    PHOTO_PERMISSION_CHOICES = (
        (PHOTO_OK, 'Tilladelse givet'),
        (PHOTO_NOTOK, 'Ikke tilladt'),
    )
    photo_permission = models.CharField('Foto tilladelse', max_length=2, choices=PHOTO_PERMISSION_CHOICES, default=PHOTO_NOTOK)
    contact_visible = models.BooleanField('Kontaktoplysninger synlige for andre holddeltagere', default=False)
    def __str__(self):
        return self.member.__str__() + ', ' + self.activity.name
    def paid(self):
        # not paid if unconfirmed payments on this activity participation
        return not Payment.objects.filter(activityparticipant=self, confirmed_dtm=None)
    def get_payment_link(self):
        payment = Payment.objects.get(activityparticipant=self, confirmed_dtm=None)
        if(payment.payment_type==Payment.CREDITCARD):
            return payment.get_quickpaytransaction().get_link_url()
        else:
            return 'javascript:alert("Kan ikke betales her:  Kontakt Coding Pirates for hjælp");'
    def save(self, *args, **kwargs):
        ''' On creation if seasonal - clear all waiting lists '''
        if not self.id:
            if self.activity.is_season():
                # remove from all waiting lists
                WaitingList.objects.filter(person=self.member.person).delete()
        return super(ActivityParticipant, self).save(*args, **kwargs)

class Volunteer(models.Model):
    class Meta:
        verbose_name = "Frivillig"
        verbose_name_plural = "Frivillige"
    person = models.ForeignKey(Person)
    department = models.ForeignKey(Department)
    def has_certificate(self):
        return self.person.has_certificate
    added = models.DateTimeField('Start', default=timezone.now)
    removed = models.DateTimeField('Slut', blank=True, null=True, default=None)
    def __str__(self):
        return self.person.__str__()

class EmailTemplate(models.Model):
    class Meta:
        verbose_name = 'Email Skabelon'
        verbose_name_plural = 'Email Skabeloner'
    idname = models.SlugField('Unikt reference navn',max_length=50, blank=False, unique=True)
    updated_dtm = models.DateTimeField('Sidst redigeret', auto_now=True)
    name = models.CharField('Skabelon navn',max_length=200, blank=False)
    description = models.CharField('Skabelon beskrivelse',max_length=200, blank=False)
    template_help = models.TextField('Hjælp omkring template variable', blank=True)
    from_address = models.EmailField()
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

        emails = []

        for reciever in recievers:
            # each reciever must be Person, Family or string (email)

            # Note - string specifically removed. We use family.dont_send_mails to make sure
            # we dont send unwanted mails.

            if type(reciever) not in (Person, Family, Department):
                raise Exception("Reciever must be of type Person or Family not " + str(type(reciever)))

            # figure out reciever
            if(type(reciever) is str):
                #check if family blacklisted. (TODO)
                destination_address = reciever
            elif(type(reciever) is Person):
                #skip if family does not want email
                if reciever.family.dont_send_mails:
                    continue
                context['person'] = reciever
                destination_address = reciever.email
            elif(type(reciever) is Family):
                #skip if family does not want email
                if reciever.dont_send_mails:
                    continue
                context['family'] = reciever
                destination_address = reciever.email
            elif(type(reciever) is Department):
                context['department'] = reciever
                destination_address = reciever.responsible_contact

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
            emails.append(email)
        return emails


class EmailItem(models.Model):
    person = models.ForeignKey(Person, blank=True, null=True)
    family = models.ForeignKey(Family, blank=True, null=True)
    reciever = models.EmailField(null=False)
    template = models.ForeignKey(EmailTemplate, null=True)
    bounce_token = UUIDField(default=uuid.uuid4, null=False)
    activity = models.ForeignKey(Activity, null=True)
    department = models.ForeignKey(Department, blank=True, null=True)
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

        self.sent_dtm = timezone.now()
        try:
            send_mail(self.subject, self.body_text, settings.SITE_CONTACT, (destination_email,), html_message=self.body_html)
        except Exception as e:
            self.send_error = str(type(e))
            self.send_error = self.send_error + str(e)
            self.save()
            raise e # forward exception to job control

        self.save()
    def __str__(self):
        return str(self.reciever) + " '"+self.subject+"'"


class Notification(models.Model):
    family = models.ForeignKey(Family)
    email = models.ForeignKey(EmailItem)
    update_info_dtm = models.DateTimeField('Bedt om opdatering af info', blank=True, null=True)
    warned_deletion_info_dtm = models.DateTimeField('Advaret om sletning fra liste', blank=True, null=True)
    anounced_department = models.ForeignKey(Department, null=True)
    anounced_activity = models.ForeignKey(Activity, null=True)
    anounced_activity_participant = models.ForeignKey(ActivityParticipant, null=True)

class AdminUserInformation(models.Model):
    user = models.OneToOneField(User)
    departments = models.ManyToManyField(Department)

class Payment(models.Model):
    CASH = 'CA'
    BANKTRANSFER = 'BA'
    CREDITCARD = 'CC'
    REFUND = 'RE'
    DEBIT = 'DE'
    OTHER = 'OT'
    PAYMENT_METHODS = (
            (CASH, 'Kontant betaling'),
            (BANKTRANSFER, 'Bankoverførsel'),
            (CREDITCARD, 'Kreditkort'),
            (REFUND, 'Refunderet'),
            (OTHER, 'Andet')
        )
    added = models.DateTimeField('Tilføjet', default=timezone.now)
    payment_type = models.CharField('Type', blank=False, null=False, max_length=2, choices=PAYMENT_METHODS,default=CASH)
    activity = models.ForeignKey(Activity, blank=True, null=True, on_delete=models.PROTECT)
    activityparticipant = models.ForeignKey(ActivityParticipant, blank=True, null=True, on_delete=models.PROTECT) # unlink if failed and new try is made
    person = models.ForeignKey(Person, blank=True, null=True, on_delete=models.PROTECT)
    family = models.ForeignKey(Family, blank=False, null=False, on_delete=models.PROTECT)
    body_text = models.TextField('Beskrivelse', blank=False)
    amount_ore = models.IntegerField('Beløb i øre', blank=False, null=False, default=0) # payments to us is positive
    confirmed_dtm = models.DateTimeField('Bekræftet', blank=True, null=True) # Set when paid (and checked)
    cancelled_dtm = models.DateTimeField('Annulleret', blank=True, null=True) # Set when transaction is cancelled
    refunded_dtm = models.DateTimeField('Refunderet', blank=True, null=True) # Set when transaction is cancelled
    rejected_dtm = models.DateTimeField('Afvist', blank=True, null=True) # Set if paiment failed
    rejected_message = models.TextField('Afvist årsag', blank=True, null=True) # message describing failure

    def save(self, *args, **kwargs):
        is_new = not self.pk # set when calling super, which is needed before we can link to this
        super_return = super(Payment, self).save(*args, **kwargs)

        ''' On creation make quickpay transaction if paymenttype CREDITCARD '''
        if(is_new and self.payment_type == Payment.CREDITCARD):
            quickpay_transaction = QuickpayTransaction(payment=self, amount_ore=self.amount_ore)
            quickpay_transaction.save()
        return super_return
    def __str__(self):
        return str(self.family.email) + " - " + self.body_text
    def get_quickpaytransaction(self):
        return self.quickpaytransaction_set.order_by('-payment__added')[0]

    def set_confirmed(self):
        if self.confirmed_dtm == None:
            self.confirmed_dtm = timezone.now()
            self.rejected_dtm = None
            self.rejected_message = None
            self.save()

    def set_rejected(self, message):
        if self.rejected_dtm == None:
            self.confirmed_dtm = None
            self.rejected_dtm = timezone.now()
            self.rejected_message = message
            self.save()

class QuickpayTransaction(models.Model):
    payment = models.ForeignKey(Payment)
    link_url =  models.CharField('Link til Quickpay formular',max_length=512, blank=True)
    transaction_id = models.IntegerField('Transaktions ID', null=True, default=None)
    refunding = models.ForeignKey('self', null=True, default=None, on_delete=models.PROTECT)
    amount_ore = models.IntegerField('Beløb i øre', default=0) # payments to us is positive
    order_id = models.CharField('Quickpay order id',max_length=20, blank=True, unique=True)

    def save(self, *args, **kwargs):
        ''' On creation make quickpay order_id from payment id '''
        if(self.pk is None):
            if settings.DEBUG:
                prefix = 'test'
            else:
                prefix = 'prod'
            self.order_id = prefix + '%06d' % self.payment.pk
        return super(QuickpayTransaction, self).save(*args, **kwargs)

    # method requests payment URL from Quickpay.
    # return_url is the url which Quickpay redirects to (used for both success and failure)
    def get_link_url(self, return_url=''):
        if(self.link_url == ''):
            #request only if not already requested
            client = QPClient(":{0}".format(settings.QUICKPAY_API_KEY))

            parent = self.payment.family.get_first_parent()

            address = {'name' : parent.name,
                       'street' : parent.address(),
                       'city' : parent.city,
                       'zip_code' : parent.zipcode,
                       'att' : self.payment.family.email,
                       'country_code' : 'DNK'
                       }

            variables = address.copy()
            variables['family'] = self.payment.family.email
            if(self.payment.person):
                variables['person_name'] = self.payment.person.name
            if(self.payment.activity):
                variables['activity_department'] = self.payment.activity.department.name
                variables['activity_name'] = self.payment.activity.name

            try:
                if(self.transaction_id == None):
                    activity = client.post('/payments', currency='DKK', order_id=self.order_id, variables=variables, invoice_address=address, shipping_address=address)
                    self.transaction_id = activity['id']
                    self.save()

                if(self.transaction_id == None):
                    raise Exception('we did not get a transaction_id')

                link = client.put(
                    '/payments/{0}/link'.format(self.transaction_id),
                    amount=self.payment.amount_ore,
                    id=self.transaction_id,
                    continueurl=return_url,
                    cancelurl=return_url,
                    customer_email=self.payment.family.email,
                    autocapture=True
                    )

                self.link_url = link['url']
                self.save()
            except:
                # Something went wrong talking to quickpay - ask people to come back later
                return reverse('payment_gateway_error_view', kwargs={'unique':self.payment.family.unique})

        return self.link_url

    # If callback was lost - we can get transaction status directly
    def update_status(self):
        client = QPClient(":{0}".format(settings.QUICKPAY_API_KEY))

        # get payment id from order id
        transactions = client.get('/payments', order_id=self.order_id)

        if(len(transactions) > 0):
            transaction = transactions[0]

            if transaction['state'] == 'processed' and transaction['accepted']:
                self.payment.set_confirmed()
            if transaction['state'] == 'rejected' and not transaction['accepted']:
                self.payment.set_rejected(repr(transaction))

    def __str__(self):
        return str(self.payment.family.email) + " - QuickPay orderid: '" + str(self.order_id) + "' confirmed: '" + str(self.payment.confirmed_dtm) + "'"


class Equipment(models.Model):
    class Meta:
        verbose_name = 'Udstyr'
        verbose_name_plural = 'Udstyr'
    created_dtm = models.DateTimeField('Oprettet', auto_now_add=True)
    title = models.CharField('Titel', max_length=200, blank=False, null=False)
    brand = models.CharField('Mærke', max_length=200, blank=True, null=True, default=None)
    model = models.CharField('Model', max_length=200, blank=True, null=True, default=None)
    serial = models.CharField('Serienummer', max_length=200, blank=True, null=True, default=None)

    count = models.IntegerField('Antal enheder', default=1, blank=False, null=False)
    link = models.URLField('Link til mere info', blank=True)
    notes = models.TextField('Generelle noter', blank=True)
    buy_price = models.DecimalField('Købs pris', max_digits=10, decimal_places=2, blank=True, null=True)
    buy_place = models.TextField('Købs sted', null=True, blank=True)
    buy_date = models.DateField('Købs dato', null=True, blank=True)
    department = models.ForeignKey(Department, blank=True, null=True)
    union = models.ForeignKey(Union, blank=True, null=True)
    def __str__(self):
        return self.title
    def clean(self):
        # Make sure equipment is owned by someone
        if(self.department == None and self.union == None):
            raise ValidationError('Udfyld ejer afdeling, forening eller begge');
        if(self.department != None and self.union != None):
            if(self.department.union != self.union):
                raise ValidationError('Afdelingen der er valgt er ikke i den valgte forening');
    def save(self, *args, **kwargs):
        if(self.union == None):
            self.union = self.department.union
        return super(Equipment, self).save(*args, **kwargs)


class EquipmentLoan(models.Model):
    class Meta:
        verbose_name = 'Udstyrs udlån'
        verbose_name_plural = 'Udstyrs udlån'
    equipment = models.ForeignKey(Equipment, blank=False, null=False)
    count = models.IntegerField('Antal enheder udlånt', default=1, blank=False, null=False)
    loaned_dtm = models.DateField('Udlånt', auto_now_add=True, null=False, blank=False)
    expected_back_dtm = models.DateField('Forventet returneret', null=True, blank=True)
    returned_dtm = models.DateField('Afleveret', null=True, blank=True)
    person = models.ForeignKey(Person, blank=False, null=False)
    department = models.ForeignKey(Department, blank=False, null=False)
    note = models.TextField('Noter', null=True, blank=True)
    def __str__(self):
        return self.equipment.title + " er lånt ud til " + self.person.name + " - " + self.department.name


class ZipcodeRegion(models.Model):
    REGION_CHOICES = (
        ('DK01' , 'Hovedstaden'),
        ('DK02' , 'Sjælland'),
        ('DK03' , 'Syddanmark'),
        ('DK04' , 'Midtjylland'),
        ('DK05' , 'Nordjylland')
    )
    region = models.CharField('Region', blank=False, null=False, max_length=4, choices=REGION_CHOICES)
    zipcode = models.CharField('Postnummer',max_length=4)
    city = models.CharField('By', max_length=200)
    municipalcode = models.IntegerField('Kommunekode', blank=False, null=False)
    municipalname = models.TextField('Kommunenavn', null=False, blank=False)

# more stat ideas: age, region distribution
class DailyStatisticsDepartment(models.Model):
    timestamp = models.DateTimeField('Kørsels tidspunkt', null=False, blank=False, default=datetime.now)
    department = models.ForeignKey(Department)
    active_activities = models.IntegerField('Aktiviteter der er igang', null=False, blank=False, default=0)
    activities = models.IntegerField('Aktiviteter i alt', null=False, blank=False, default=0)
    current_activity_participants = models.IntegerField('Deltagere på aktiviteter', null=False, blank=False, default=0)
    activity_participants = models.IntegerField('Deltagere på aktiviteter over al tid', null=False, blank=False, default=0)
    members = models.IntegerField('Medlemmer', null=False, blank=False, default=0)
    waitinglist = models.IntegerField('Venteliste', null=False, blank=False, default=0)
    waitingtime = models.DurationField('Ventetid', null=False, blank=False, default=0)
    payments = models.IntegerField('Betalinger', null=False, blank=False, default=0)
    volunteers_male = models.IntegerField('Frivillige Mænd', null=False, blank=False, default=0)
    volunteers_female = models.IntegerField('Frivillige Kvinder', null=False, blank=False, default=0)
    volunteers = models.IntegerField('Frivillige', null=False, blank=False, default=0)

class DailyStatisticsUnion(models.Model):
    timestamp = models.DateTimeField('Kørsels tidspunkt', null=False, blank=False, default=datetime.now)
    union = models.ForeignKey(Union)
    departments = models.IntegerField('Afdelinger', null=False, blank=False, default=0)
    active_activities = models.IntegerField('Aktiviteter der er igang', null=False, blank=False, default=0)
    activities = models.IntegerField('Aktiviteter i alt', null=False, blank=False, default=0)
    current_activity_participants = models.IntegerField('Deltagere på aktiviteter', null=False, blank=False, default=0)
    activity_participants = models.IntegerField('Deltagere på aktiviteter over al tid', null=False, blank=False, default=0)
    members = models.IntegerField('Medlemmer', null=False, blank=False, default=0)
    waitinglist = models.IntegerField('Venteliste', null=False, blank=False, default=0)
    payments = models.IntegerField('Betalinger', null=False, blank=False, default=0)
    volunteers_male = models.IntegerField('Frivillige Mænd', null=False, blank=False, default=0)
    volunteers_female = models.IntegerField('Frivillige Kvinder', null=False, blank=False, default=0)
    volunteers = models.IntegerField('Frivillige', null=False, blank=False, default=0)

class DailyStatisticsRegion(models.Model):
    timestamp = models.DateTimeField('Kørsels tidspunkt', null=False, blank=False, default=datetime.now)
    region = models.CharField('Region', blank=False, null=False, max_length=4, choices=ZipcodeRegion.REGION_CHOICES)
    departments = models.IntegerField('Afdelinger', null=False, blank=False, default=0)
    active_activities = models.IntegerField('Aktiviteter der er igang', null=False, blank=False, default=0)
    activities = models.IntegerField('Aktiviteter i alt', null=False, blank=False, default=0)
    current_activity_participants = models.IntegerField('Deltagere på aktiviteter', null=False, blank=False, default=0)
    activity_participants = models.IntegerField('Deltagere på aktiviteter over al tid', null=False, blank=False, default=0)
    members = models.IntegerField('Medlemmer', null=False, blank=False, default=0)
    waitinglist = models.IntegerField('Venteliste', null=False, blank=False, default=0)
    payments = models.IntegerField('Betalinger', null=False, blank=False, default=0)
    volunteers_male = models.IntegerField('Frivillige Mænd', null=False, blank=False, default=0)
    volunteers_female = models.IntegerField('Frivillige Kvinder', null=False, blank=False, default=0)
    volunteers = models.IntegerField('Frivillige', null=False, blank=False, default=0)

class DailyStatisticsGeneral(models.Model):
    timestamp = models.DateTimeField('Kørsels tidspunkt', null=False, blank=False, default=datetime.now)
    persons = models.IntegerField('Personer', null=False, blank=False, default=0)
    children_male = models.IntegerField('Børn Drenge', null=False, blank=False, default=0)
    children_female = models.IntegerField('Børn Piger', null=False, blank=False, default=0)
    children = models.IntegerField('Børn', null=False, blank=False, default=0)
    volunteers_male = models.IntegerField('Frivillige Mænd', null=False, blank=False, default=0)
    volunteers_female = models.IntegerField('Frivillige Kvinder', null=False, blank=False, default=0)
    volunteers = models.IntegerField('Frivillige', null=False, blank=False, default=0)
    departments = models.IntegerField('Afdelinger', null=False, blank=False, default=0)
    unions = models.IntegerField('Lokalforeninger', null=False, blank=False, default=0)
    waitinglist_male = models.IntegerField('Drenge på venteliste', null=False, blank=False, default=0)
    waitinglist_female = models.IntegerField('Piger på venteliste', null=False, blank=False, default=0)
    waitinglist = models.IntegerField('Personer på venteliste', null=False, blank=False, default=0)
    family_visits = models.IntegerField('Profilsider besøgt foregående 24 timer', null=False, blank=False, default=0)
    dead_profiles = models.IntegerField('Profilsider efterladt over et år', null=False, blank=False, default=0)
    current_activity_participants = models.IntegerField('Deltagere på aktiviteter', null=False, blank=False, default=0)
    activity_participants = models.IntegerField('Deltagere på aktiviteter over al tid', null=False, blank=False, default=0)
    activity_participants_male = models.IntegerField('Deltagere på aktiviteter over al tid (drenge)', null=False, blank=False, default=0)
    activity_participants_female = models.IntegerField('Deltagere på aktiviteter over al tid (piger)', null=False, blank=False, default=0)
    payments = models.IntegerField('Betalinger sum', null=False, blank=False, default=0)
    payments_transactions = models.IntegerField('Betalinger transaktioner', null=False, blank=False, default=0)

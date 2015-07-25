#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django_extensions.db.fields import UUIDField
import uuid
import datetime
from django.template import Engine, Context
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
from quickpay import QPClient


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
        verbose_name = 'familie'
        verbose_name_plural = 'Familier'
        permissions = (
            ("view_family_unique", "Can view family UUID field (password) - gives access to address"),
        )

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
    def send_link_email(self,):
        EmailTemplate.objects.get(idname = 'LINK').makeEmail(self, {})

class Person(models.Model):
    class Meta:
        verbose_name_plural='Personer'
        ordering=['name']
        permissions = (
            ("view_full_address", "Can view persons full address + phonenumber + email"),
        )

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
    MALE = 'MA'
    FEMALE = 'FM'
    MEMBER_GENDER_CHOICES = (
        (MALE, 'Dreng'),
        (FEMALE, 'Pige')
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
        return format_address(self.streetname, self.housenumber, self.floor, self.door)
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    gender = models.CharField('Køn',max_length=20,choices=MEMBER_GENDER_CHOICES,default=None, null=True)
    birthday = models.DateField('Fødselsdag', blank=True, null=True)
    has_certificate = models.DateField('Børneattest',blank=True, null=True)
    family = models.ForeignKey(Family)
    added = models.DateTimeField('Tilføjet', default=timezone.now, blank=False)
    deleted_dtm = models.DateTimeField('Slettet', null=True, blank=True)
    def __str__(self):
        return self.name

    def age_years(self):
        if(self.birthday != None):
            return (timezone.now().date() - self.birthday).days // 365
        else:
            return 0
    age_years.admin_order_field = '-birthday'
    age_years.short_description = 'Alder'


class Department(models.Model):
    class Meta:
        verbose_name_plural='Afdelinger'
        verbose_name='afdeling'
        ordering=['name']
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
    has_waiting_list = models.BooleanField('Venteliste',default=False)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    def no_members(self):
        return self.member_set.count()
    no_members.short_description = 'Antal medlemmer'
    def __str__(self):
        return self.name
    def address(self):
        return format_address(self.streetname, self.housenumber, self.floor, self.door)

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
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
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
        verbose_name='aktivitet'
        verbose_name_plural = 'Aktiviteter'
        ordering =['start_date']
    department = models.ForeignKey(Department)
    name = models.CharField('Navn',max_length=200)
    open_hours = models.CharField('Tidspunkt',max_length=200)
    responsible_name = models.CharField('Afdelingsleder',max_length=200)
    responsible_contact = models.EmailField('E-mail')
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    zipcode = models.CharField('Postnummer',max_length=4)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn',max_length=200)
    housenumber = models.CharField('Husnummer',max_length=200)
    floor = models.CharField('Etage',max_length=200, blank=True)
    door = models.CharField('Dør',max_length=200, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    description = models.TextField('Beskrivelse', blank=True)
    instructions = models.TextField('Tilmeldings instruktioner', blank=True)
    start_date = models.DateField('Start')
    end_date = models.DateField('Slut')
    signup_closing = models.DateField('Tilmelding lukker', null=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    open_invite = models.BooleanField('Fri tilmelding', default=False)
    price = models.IntegerField('Pris (øre)', blank=True, null=True, default=None)
    max_participants = models.PositiveIntegerField('Max Holdstørrelse', default=30)
    def is_historic(self):
        return self.end_date < datetime.date.today()
    is_historic.short_description = 'Historisk?'
    def __str__(self):
        return self.department.name + ", " + self.name
    def save(self, *args,**kwargs):
        ''' Validate price is not between 999 and 1
        (would be 0,01 to 9,99 kr and probaly forgot to specify in øre'''
        if self.price is not None and self.price < 999 and self.price > 1:
            raise Exception("Seems like price was specified in Kroner, not Øre")
        return super(Activity, self).save(*args, **kwargs)


class ActivityInvite(models.Model):
    class Meta:
        verbose_name='invitation'
        verbose_name_plural = 'Invitationer'
    activity = models.ForeignKey(Activity)
    person = models.ForeignKey(Person)
    invite_dtm = models.DateField('Inviteret', default=timezone.now)
    expire_dtm = models.DateField('Udløber')
    rejected_dtm = models.DateField('Afslået', blank=True, null=True)
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

class Volunteer(models.Model):
    member = models.ForeignKey(Member)
    department = models.ForeignKey(Department)
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

class AdminUserInformation(models.Model):
    user = models.OneToOneField(User)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

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
            self.order_id = 'test%06d' % self.payment.pk
        return super(QuickpayTransaction, self).save(*args, **kwargs)

    # method requests payment URL from Quickpay.
    # return_url is the url which Quickpay redirects to (used for both success and failure)
    def get_link_url(self, return_url=''):
        if(self.link_url == ''):
            #request only if not already requested
            client = QPClient(":{0}".format(settings.QUICKPAY_API_KEY))

            activity = client.post('/payments', currency='DKK', order_id=self.order_id)
            self.transaction_id = activity['id']
            self.save()

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

        return self.link_url

    def __str__(self):
        return str(self.payment.family.email) + " - QuickPay orderid: '" + str(self.order_id) + "' confirmed: '" + str(self.payment.confirmed_dtm) + "'"

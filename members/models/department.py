from django.db import models
import members.models.emailtemplate
from members.utils.address import format_address
from django.contrib.auth.models import User
from django.utils import timezone, html
import requests
import json


class Department(models.Model):
    class Meta:
        verbose_name_plural = 'Afdelinger'
        verbose_name = 'Afdeling'
        ordering = ['zipcode']
    name = models.CharField('Navn', max_length=200)
    description = models.TextField('Beskrivelse af afdeling', blank=True)
    open_hours = models.CharField('Åbningstid', max_length=200, blank=True)
    responsible_name = models.CharField('Afdelingsleder', max_length=200, blank=True)
    responsible_contact = models.EmailField('E-mail', blank=True)
    placename = models.CharField('Stednavn', max_length=200, blank=True)
    zipcode = models.CharField('Postnummer', max_length=10)
    city = models.CharField('By', max_length=200)
    streetname = models.CharField('Vejnavn', max_length=200)
    housenumber = models.CharField('Husnummer', max_length=10)
    floor = models.CharField('Etage', max_length=10, blank=True)
    door = models.CharField('Dør', max_length=10, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    has_waiting_list = models.BooleanField('Venteliste', default=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    created = models.DateField('Oprettet', blank=False, default=timezone.now)
    closed_dtm = models.DateField('Lukket', blank=True, null=True, default=None)
    isVisible = models.BooleanField('Kan ses på afdelingssiden', default=True)
    isOpening = models.BooleanField('Er afdelingen under opstart', default=False)
    website = models.URLField('Hjemmeside', blank=True)
    union = models.ForeignKey('Union', verbose_name="Lokalforening", blank=False, null=False)
    longtitude = models.DecimalField("Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6)
    latitude = models.DecimalField("Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6)
    onMap = models.BooleanField("Skal den være på kortet?", default=True)

    def no_members(self):
        return self.member_set.count()
    no_members.short_description = 'Antal medlemmer'

    def __str__(self):
        return self.name

    def address(self):
        return format_address(self.streetname, self.housenumber, self.floor, self.door)

    def address_with_zip(self):
        return self.address() + ", " + self.zipcode + " " + self.city

    def to_html(self):
        my_html = ''
        if self.website == '':
            my_html += '<strong>Coding Pirates ' + html.escape(self.name) + '</strong><br>'
        else:
            my_html += '<a href="' + html.escape(self.website) + '">' + '<strong>Coding Pirates ' + html.escape(self.name) + '</strong></a><br>'
        if self.isOpening:
            my_html += "<strong>Afdelingen slår snart dørene op!</strong><br>"
        if self.placename != '':
            my_html += html.escape(self.placename) + '<br>'
        my_html += html.escape(self.address()) + '<br>' + html.escape(self.zipcode) + ", " + html.escape(self.city) + '<br>'
        my_html += 'Afdelingsleder: ' + html.escape(self.responsible_name) + '<br>'
        my_html += 'E-mail: <a href="mailto:' + html.escape(self.responsible_contact) + '">' + html.escape(self.responsible_contact) + '</a><br>'
        my_html += 'Tidspunkt: ' + html.escape(self.open_hours)

        return my_html

    def get_long_lat(self):
        if self.latitude is None or self.longtitude is None:
            addressID = 0
            dist = 0
            req = 'https://dawa.aws.dk/datavask/adresser?betegnelse=' + self.address_with_zip().replace(" ", "%20")
            try:
                washed = json.loads(requests.get(req).text)
                addressID = washed['resultater'][0]['adresse']['id']
                dist = washed['resultater'][0]['vaskeresultat']['afstand']
            except Exception as error:
                print("Couldn't find addressID for " + self.name)
                print("Error " + str(error))
            if (addressID != 0 and dist < 10):
                try:
                    req = 'https://dawa.aws.dk/adresser/' + addressID + "?format=geojson"
                    address = json.loads(requests.get(req).text)
                    self.latitude = address['geometry']['coordinates'][0]
                    self.longtitude = address['geometry']['coordinates'][1]
                    self.save()
                    print("Opdateret for " + self.name)
                    print("Updated coordinates for " + self.name)
                    return(self.latitude, self.longtitude)
                except Exception as error:
                    print("Couldn't find coordinates for " + self.name)
                    print("Error " + str(error))
        else:
            return(self.latitude, self.longtitude)

    def new_volunteer_email(self, volunteer_name):
        # First fetch department leaders email
        new_vol_email = members.models.emailtemplate.EmailTemplate.objects.get(idname='VOL_NEW')
        context = {
            'department': self,
            'volunteer_name': volunteer_name,
        }
        new_vol_email.makeEmail(self, context)


class AdminUserInformation(models.Model):
    user = models.OneToOneField(User)
    departments = models.ManyToManyField(Department)

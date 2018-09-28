#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from members.utils.address import format_address
from urllib.parse import quote_plus
import requests
import json


class Person(models.Model):
    class Meta:
        verbose_name = "Person"
        verbose_name_plural = 'Personer'
        ordering = ['added']
        permissions = (
            ("view_full_address", "Can view persons full address + phonenumber + email"),
            ("view_all_persons", "Can view persons not related to department"),
        )

    PARENT = 'PA'
    GUARDIAN = 'GU'
    CHILD = 'CH'
    OTHER = 'NA'
    MEMBER_TYPE_CHOICES = (
        (PARENT, 'Forælder'),
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
    membertype = models.CharField('Type', max_length=2,
                                  choices=MEMBER_TYPE_CHOICES, default=PARENT)
    name = models.CharField('Navn', max_length=200)
    zipcode = models.CharField('Postnummer', max_length=4, blank=True)
    city = models.CharField('By', max_length=200, blank=True)
    streetname = models.CharField('Vejnavn', max_length=200, blank=True)
    housenumber = models.CharField('Husnummer', max_length=5, blank=True)
    floor = models.CharField('Etage', max_length=3, blank=True)
    door = models.CharField('Dør', max_length=5, blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    municipality = models.CharField('Kommune', max_length=100, blank=True, null=True)
    longitude = models.DecimalField('Længdegrad', blank=True, null=True, max_digits=9, decimal_places=6)
    latitude = models.DecimalField('Breddegrad', blank=True, null=True, max_digits=9, decimal_places=6)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    placename = models.CharField('Stednavn', max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    gender = models.CharField('Køn', max_length=20,
                              choices=MEMBER_GENDER_CHOICES, default=None,
                              null=True)
    birthday = models.DateField('Fødselsdag', blank=True, null=True)
    has_certificate = models.DateField('Børneattest', blank=True, null=True)
    family = models.ForeignKey('Family')
    notes = models.TextField('Noter', blank=True, null=False, default="")
    added = models.DateTimeField('Tilføjet', default=timezone.now, blank=False)
    deleted_dtm = models.DateTimeField('Slettet', null=True, blank=True)

    def __str__(self):
        return self.name

    def address(self):
        return format_address(self.streetname, self.housenumber, self.floor, self.door)

    def addressWithZip(self):
        return self.address() + ", " + self.zipcode + " " + self.city

    def age_from_birthdate(self, date):
        today = timezone.now().date()
        return today.year - date.year - ((today.month, today.day) < (date.month, date.day))

    def age_years(self):
        if(self.birthday is not None):
            return self.age_from_birthdate(self.birthday)
        else:
            return 0
    age_years.admin_order_field = '-birthday'
    age_years.short_description = 'Alder'

    def firstname(self):
        return self.name.partition(' ')[0]

    def update_dawa_data(self):
        if(self.dawa_id is None or
           self.latitude is None or
           self.longitude is None or
           self.municipality is None):
            addressID = 0
            dist = 0
            req = 'https://dawa.aws.dk/datavask/adresser?betegnelse='
            req += quote_plus(self.addressWithZip())
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
                    self.longitude = address['geometry']['coordinates'][0]
                    self.latitude = address['geometry']['coordinates'][1]
                    self.municipality = address['properties']['kommunenavn']
                    self.dawa_id = address['properties']['id']
                    self.save()
                    print("Opdateret for " + self.name)
                    print("Updated coordinates for " + self.name)
                    print("Updated municipality for " + self.name)
                except Exception as error:
                    print("Couldn't find coordinates for " + self.name)
                    print("Error " + str(error))
                    return None
    # TODO: Move to dawa_data in utils

    firstname.admin_order_field = 'name'
    firstname.short_description = 'Fornavn'

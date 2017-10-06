#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from members.utils.address import format_address


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
    address_line2 = models.CharField('Adresselinje 2', max_length=200, help_text="Skriv CO-adresse her", blank=True)
    dawa_id = models.CharField('DAWA id', max_length=200, blank=True)
    updated_dtm = models.DateTimeField('Opdateret', auto_now=True)
    placename = models.CharField('Stednavn',max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    gender = models.CharField('Køn',max_length=20,choices=MEMBER_GENDER_CHOICES,default=None, null=True)
    birthday = models.DateField('Fødselsdag', blank=True, null=True)
    has_certificate = models.DateField('Børneattest',blank=True, null=True)
    family = models.ForeignKey('Family')
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
        if(self.birthday is not None):
            return self.age_from_birthdate(self.birthday)
        else:
            return 0
    age_years.admin_order_field = '-birthday'
    age_years.short_description = 'Alder'

    def firstname(self):
        return self.name.partition(' ')[0]
    firstname.admin_order_field = 'name'
    firstname.short_description = 'Fornavn'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from members.utils.address import format_address
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from members.managers import UserManager
from django.utils.translation import ugettext_lazy as _


class Person(AbstractBaseUser, PermissionsMixin):
    class Meta:
        swappable = 'AUTH_USER_MODEL'
        verbose_name = "Person"
        verbose_name_plural='Personer'
        ordering=['added']
        permissions = (
            ("view_full_address", "Can view persons full address + phonenumber + email"),
            ("view_all_persons", "Can view persons not related to department"),
        )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = (
        'membertype',
        'name',
        'family'
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
    email = models.EmailField(blank=True, unique=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    gender = models.CharField('Køn',max_length=20,choices=MEMBER_GENDER_CHOICES,default=None, null=True)
    birthday = models.DateField('Fødselsdag', blank=True, null=True)
    has_certificate = models.DateField('Børneattest',blank=True, null=True)
    family = models.ForeignKey('Family')
    notes = models.TextField('Noter', blank=True, null=False, default ="")
    added = models.DateTimeField('Tilføjet', default=timezone.now, blank=False)
    deleted_dtm = models.DateTimeField('Slettet', null=True, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

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

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.partition(' ')[0]

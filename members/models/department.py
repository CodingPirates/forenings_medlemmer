#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.emailtemplate
from django.utils import timezone, html


class Department(models.Model):
    class Meta:
        verbose_name_plural = "Afdelinger"
        verbose_name = "Afdeling"
        ordering = ["zipcode"]

    help_dept = """Vi tilføjer automatisk "Coding Pirates" foran navnet når vi
    nævner det de fleste steder på siden."""
    name = models.CharField("Navn", max_length=200, help_text=help_dept)
    description = models.TextField("Beskrivelse af afdeling", blank=True)
    open_hours = models.CharField("Åbningstid", max_length=200, blank=True)
    responsible_name = models.CharField("Afdelingsleder", max_length=200, blank=True)
    responsible_contact = models.EmailField("E-mail", blank=True)
    address = models.ForeignKey(
        "Address", on_delete=models.PROTECT, null=True, blank=True
    )
    placename = models.CharField("Stednavn", max_length=200, blank=True)
    zipcode = models.CharField("Postnummer", max_length=10)
    city = models.CharField("By", max_length=200)
    streetname = models.CharField("Vejnavn", max_length=200)
    housenumber = models.CharField("Husnummer", max_length=10)
    floor = models.CharField("Etage", max_length=10, blank=True)
    door = models.CharField("Dør", max_length=10, blank=True)
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)
    has_waiting_list = models.BooleanField("Venteliste", default=True)
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)
    created = models.DateField("Oprettet", blank=False, default=timezone.now)
    closed_dtm = models.DateField("Lukket", blank=True, null=True, default=None)
    isVisible = models.BooleanField("Kan ses på afdelingssiden", default=True)
    isOpening = models.BooleanField("Er afdelingen under opstart", default=False)
    website = models.URLField("Hjemmeside", blank=True)
    union = models.ForeignKey(
        "Union", verbose_name="Lokalforening", on_delete=models.PROTECT,
    )
    longitude = models.DecimalField(
        "Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        "Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    onMap = models.BooleanField("Skal den være på kortet?", default=True)

    def no_members(self):
        return self.member_set.count()

    no_members.short_description = "Antal medlemmer"

    def __str__(self):
        return self.name

    def toHTML(self):
        myHTML = ""
        if self.website == "":
            myHTML += (
                "<strong>Coding Pirates " + html.escape(self.name) + "</strong><br>"
            )
        else:
            myHTML += (
                '<a href="'
                + html.escape(self.website)
                + '">'
                + "<strong>Coding Pirates "
                + html.escape(self.name)
                + "</strong></a><br>"
            )
        if self.isOpening:
            myHTML += "<strong>Afdelingen slår snart dørene op!</strong><br>"
        if self.placename != "":
            myHTML += html.escape(self.placename) + "<br>"
        myHTML += (
            html.escape(str(self))
            + "<br>"
            + html.escape(self.zipcode)
            + ", "
            + html.escape(self.city)
            + "<br>"
        )
        myHTML += "Afdelingsleder: " + html.escape(self.responsible_name) + "<br>"
        myHTML += (
            'E-mail: <a href="mailto:'
            + html.escape(self.responsible_contact)
            + '">'
            + html.escape(self.responsible_contact)
            + "</a><br>"
        )
        myHTML += "Tidspunkt: " + html.escape(self.open_hours)
        return myHTML

    def new_volunteer_email(self, volunteer_name):
        # First fetch department leaders email
        new_vol_email = members.models.emailtemplate.EmailTemplate.objects.get(
            idname="VOL_NEW"
        )
        context = {"department": self, "volunteer_name": volunteer_name}
        new_vol_email.makeEmail(self, context)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class Activity(models.Model):
    class Meta:
        verbose_name = "Aktivitet"
        verbose_name_plural = "Aktiviteter"
        ordering = ["department__address__zipcode", "start_date"]

    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    union = models.ForeignKey("Union", blank=True, on_delete=models.CASCADE, default=1)
    name = models.CharField("Navn", max_length=200)
    open_hours = models.CharField("Tidspunkt", max_length=200)
    responsible_name = models.CharField("Ansvarlig", max_length=200)
    responsible_contact = models.EmailField("E-mail")
    placename = models.CharField("Stednavn", max_length=200, blank=True, null=True)
    zipcode = models.CharField("Postnummer", max_length=4)
    city = models.CharField("By", max_length=200)
    streetname = models.CharField("Vejnavn", max_length=200)
    housenumber = models.CharField("Husnummer", max_length=200)
    floor = models.CharField("Etage", max_length=200, blank=True, null=True)
    door = models.CharField("Dør", max_length=200, blank=True, null=True)
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)
    description = models.TextField("Beskrivelse", blank=False)
    instructions = models.TextField("Tilmeldings instruktioner", blank=True)
    start_date = models.DateField("Start")
    end_date = models.DateField("Slut")
    signup_closing = models.DateField("Tilmelding lukker", null=True)
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)
    open_invite = models.BooleanField("Fri tilmelding", default=False)
    help_price = "På prisen for aktiviteten fratrækker vi automatisk 75 kr."
    help_price += " pr. barn hvis det er en sæsonaktivitet."
    price_in_dkk = models.DecimalField(
        "Pris", max_digits=10, decimal_places=2, default=500, help_text=help_price
    )
    max_participants = models.PositiveIntegerField("Max deltagere", default=30)
    max_age = models.PositiveIntegerField("Maximum Alder", default=17)
    min_age = models.PositiveIntegerField("Minimum Alder", default=7)
    help_temp = "Bestemmer om personerne bliver til medlemmer i forhold til DUF."
    help_temp += " De fleste aktiviteter er sæsoner og medlemsberettiget. Hvis "
    help_temp += "du er i tvivl, så spørg på Slack i #medlemsssystem-support."
    member_justified = models.BooleanField(
        "Aktiviteten gør personen til medlem", default=True, help_text=help_temp
    )

    def is_historic(self):
        return self.end_date < timezone.now()

    is_historic.short_description = "Historisk?"

    def __str__(self):
        return self.department.name + ", " + self.name

    def is_season(self):
        return (self.end_date - self.start_date).days > 30

    def will_reserve(self):
        return self.start_date.year > timezone.now().year

    def seats_left(self):
        return self.max_participants - self.activityparticipant_set.count()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Activity(models.Model):
    class Meta:
        verbose_name = "Aktivitet"
        verbose_name_plural = "Aktiviteter"
        ordering = ["department__address__zipcode", "start_date"]

    department = models.ForeignKey(
        "Department", on_delete=models.CASCADE, verbose_name="Afdeling"
    )
    # Please note: Activity.Union is used as a hack for the Foreningsmedlemskab / Støttemedlemskab
    # It's not used for anything else
    union = models.ForeignKey(
        "Union",
        on_delete=models.CASCADE,
        default=1,
        verbose_name="Forening",
    )
    name = models.CharField("Navn", max_length=200)
    activitytype = models.ForeignKey(
        "ActivityType",
        on_delete=models.CASCADE,
        default="FORLØB",
        verbose_name="Aktivitetstype",
        help_text="""Angiv typen af aktivtet.
        Brugere vil se Forløb og Arrangementer under Aktiviteter.
        Medlemskab og Støttemedlemskab vil blive vist på separate sider.
        Normalt vil det kun være sekretariatet der oprettet aktiviteter for medlemskaber.""",
    )
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
    help_price = """Hvis det er et forløb / en sæsonaktivitet fratrækkes der automatisk 100 kr.
            til Coding Pirates Denmark pr. barn."""
    price_in_dkk = models.DecimalField(
        "Pris", max_digits=10, decimal_places=2, default=500, help_text=help_price
    )
    max_participants = models.PositiveIntegerField("Max deltagere", default=30)
    max_age = models.PositiveIntegerField("Maximum Alder", default=17)
    min_age = models.PositiveIntegerField("Minimum Alder", default=7)
    help_text = """Bestemmer om personerne bliver til medlem i forhold til DUF.
        De fleste aktiviteter er forløb/sæsoner og medlemsberettiget. Hvis
        du er i tvivl, så spørg på Slack i #medlemsssystem-support."""
    member_justified = models.BooleanField(
        "Aktiviteten gør personen til medlem", default=True, help_text=help_text
    )

    def is_historic(self):
        return self.end_date < timezone.now()

    is_historic.short_description = "Historisk?"

    def __str__(self):
        return self.department.name + ", " + self.name

    def filterinfo(self):
        return self.department.name + ": " + self.name

    def is_season(self):
        return (self.end_date - self.start_date).days > 30

    def will_reserve(self):
        return self.start_date.year > timezone.now().year

    def seats_left(self):
        return self.max_participants - self.activityparticipant_set.count()

    seats_left.short_description = "Ledige pladser"

    def participants(self):
        return self.activityparticipant_set.count()

    participants.short_description = "Deltagere"

    def clean(self):
        errors = {}
        min_amount = 0

        if self.activitytype.id == "FORENINGSMEDLEMSKAB":
            min_amount = 75

        if self.activitytype.id == "FORLØB":
            min_amount = 100

        if self.price_in_dkk < min_amount:
            errors[
                "price_in_dkk"
            ] = f"Prisen er for lav. Denne type aktivitet skal koste mindst {min_amount} kr."

        if errors:
            raise ValidationError(errors)

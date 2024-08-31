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

    MEMBERSHIP_MIN_AMOUNT = 75
    ACTIVITY_MIN_AMOUNT = 100
    NO_MINIMUM_AMOUNT = 0

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
    address = models.ForeignKey(
        "Address", on_delete=models.PROTECT, verbose_name="Adresse", null=False
    )
    visible_from = models.DateTimeField(
        "Aktiviteten er synlig fra", null=False, blank=False, default=timezone.now
    )
    visible = models.BooleanField(
        "Vises denne aktivitet",
        null=False,
        blank=False,
        default=True,
        help_text="Vises i denne aktivtet. Kan bruges sammen med feltet 'Aktiviteten er synlig fra'",
    )

    def is_historic(self):
        return self.end_date < timezone.now()

    is_historic.short_description = "Historisk?"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def __str__(self):
        return self.department.name + ", " + self.name

    def filterinfo(self):
        return self.department.name + ": " + self.name

    def is_season(self):
        return self.activitytype_id == "FORLØB"

    def is_eligable_for_membership(self):
        return (
            self.activitytype_id == "FORLØB"
            or self.activitytype_id == "FORENINGSMEDLEMSKAB"
        )

    def will_reserve(self):
        return self.start_date.year > timezone.now().year

    def seats_left(self):
        return self.max_participants - self.activityparticipant_set.count()

    seats_left.short_description = "Ledige pladser"

    def participants(self):
        return self.activityparticipant_set.count()

    participants.short_description = "Deltagere"

    def get_min_amount(self, activitytype):
        min_amount = self.NO_MINIMUM_AMOUNT

        # Issue 1058: If activity is in the past then skip this check
        # During activity creation, the end_date could have been left empty
        if self.end_date and self.end_date > timezone.now().date():
            if activitytype == "FORENINGSMEDLEMSKAB":
                min_amount = self.MEMBERSHIP_MIN_AMOUNT

            if activitytype == "FORLØB":
                min_amount = self.ACTIVITY_MIN_AMOUNT

        return min_amount

    def clean(self):
        errors = {}
        min_amount = self.get_min_amount(self.activitytype.id)

        if self.price_in_dkk < min_amount:
            errors["price_in_dkk"] = (
                f"Prisen er for lav. Denne type aktivitet skal koste mindst {min_amount} kr."
            )

        if self.signup_closing > self.end_date:
            errors["signup_closing"] = (
                "Tilmeldingsfristen skal være før aktiviteten slutter"
            )

        if errors:
            raise ValidationError(errors)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Activity(models.Model):
    class Meta:
        verbose_name = "Aktivitet"
        verbose_name_plural = "Aktiviteter"
        ordering = ["department__address__zipcode", "start_date"]

    MEMBERSHIP_MIN_AMOUNT = settings.MINIMUM_MEMBERSHIP_PRICE_IN_DKK
    ACTIVITY_MIN_AMOUNT = settings.MINIMUM_SEASON_PRICE_IN_DKK
    NO_MINIMUM_AMOUNT = settings.MINIMUM_PRICE_IN_DKK

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
        help_text="""Angiv typen af aktivitet. Brugere vil se Forløb og Arrangementer under Aktiviteter.<br>Medlemskab og Støttemedlemskab vil blive vist på separate sider.<br>Medlemskab bliver oprettet automatisk af systemet.""",
    )

    season_fee = models.DecimalField(
        "Sæsonbidrag til Coding Pirates Denmark",
        max_digits=7,
        decimal_places=2,
        default=None,
        null=True,
        blank=True,
        help_text="""Standard er 150 kr for sæson/forløb, 0 kr for Arrangementer og Støttemedlemskaber.<br>Beregnes automatisk ved oprettelse af aktiviteten.""",
    )
    season_fee_change_reason = models.CharField(
        "Begrundelse for ændring af sæsonbidrag",
        max_length=255,
        blank=True,
        help_text="Påkrævet hvis sæsonbidrag ændres fra standard.",
    )

    open_hours = models.CharField("Tidspunkt", max_length=200)
    responsible_name = models.CharField("Ansvarlig", max_length=200)
    responsible_contact = models.EmailField("E-mail")
    description = models.TextField("Beskrivelse", blank=False)
    instructions = models.TextField("Tilmeldings instruktioner", blank=True)
    start_date = models.DateField("Start")
    end_date = models.DateField("Slut")
    signup_closing = models.DateField("Tilmelding lukker", null=True)
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)
    open_invite = models.BooleanField("Fri tilmelding", default=False)
    help_price = f"Hvis det er et forløb / en sæsonaktivitet fratrækkes der automatisk {ACTIVITY_MIN_AMOUNT} kr. til Coding Pirates Denmark pr. barn."
    price_in_dkk = models.DecimalField(
        "Pris", max_digits=10, decimal_places=2, default=500, help_text=help_price
    )
    max_participants = models.PositiveIntegerField("Max deltagere", default=30)
    max_age = models.PositiveIntegerField("Maximum Alder", default=17)
    min_age = models.PositiveIntegerField("Minimum Alder", default=7)
    help_text = """Bestemmer om personerne bliver til medlem i forhold til DUF.
        De fleste aktiviteter er forløb/sæsoner og medlemsberettiget. Hvis
        du er i tvivl, så spørg på Slack i #medlemssystem_support."""
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

    def invitations(self):
        return self.activityinvite_set.count()

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

        if self.start_date is None:
            errors["start_date"] = "Der skal angives en startdato for aktiviteten"

        if self.end_date is None:
            errors["end_date"] = "Der skal angives en slutdato for aktiviteten"

        if self.signup_closing is None:
            errors["signup_closing"] = "Der skal angives en dato for tilmeldingsfrist"

        if (
            (self.start_date is not None)
            and (self.end_date is not None)
            and (self.start_date > self.end_date)
        ):
            errors["signup_closing"] = "Startdato skal være før aktivitetens slutdato"

        if (
            (self.signup_closing is not None)
            and (self.end_date is not None)
            and (self.signup_closing > self.end_date)
        ):
            errors["signup_closing"] = (
                "Tilmeldingsfristen skal være før aktiviteten slutter"
            )

        if self.max_age < self.min_age:
            errors["max_age"] = "Maksimumsalder skal være større end minimumsalder."

        if (
            self.start_date
            and self.end_date
            and self.start_date.year >= timezone.now().year
        ):
            # Validering er ikke for historiske aktiviteter
            duration = (self.end_date - self.start_date).days + 1
            if self.activitytype.id == "FORLØB" and duration <= 14:
                errors["end_date"] = "Et forløb skal vare mindst 15 dage."
            if self.activitytype.id == "ARRANGEMENT" and duration > 14:
                errors["end_date"] = "Et arrangement kan maksimalt vare 14 dage."

        if self.activitytype and self.activitytype.id == "FORLØB":
            default_fee = 150
        else:
            default_fee = 0

        if self.season_fee is None:
            self.season_fee = default_fee

        if self.season_fee is not None and self.season_fee < 0:
            errors["season_fee"] = "Sæsonbidraget kan ikke være negativt."

        if self.season_fee != default_fee and not self.season_fee_change_reason:
            errors["season_fee_change_reason"] = (
                "Du skal angive en begrundelse for at ændre sæsonbidraget."
            )

        if (
            self.activitytype
            and self.activitytype.id in ["FORENINGSMEDLEMSKAB", "STØTTEMEDLEMSKAB"]
        ) and (self.price_in_dkk != 0):
            errors["price_in_dkk"] = "Prisen for medlemskaber skal være 0 kr."

        if errors:
            raise ValidationError(errors)

    def delete(self, *args, **kwargs):
        if self.invitations() > 0 or self.participants() > 0:
            raise ValidationError(
                f'Aktivitet "{self.name}" kan ikke slettes, da der er tilmeldte eller inviterede personer. Muligvis vil systemet skrive at aktiviteten er slettet, men det er den ikke.'
            )
        super().delete(*args, **kwargs)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from members.models import Activity, ActivityParticipant, Payment
from django.utils import timezone
from datetime import timedelta
from django.db.models import F
import datetime


class Union(models.Model):
    class Meta:
        verbose_name_plural = "Foreninger"
        verbose_name = "Forening"
        ordering = ["name"]

    name = models.CharField("Foreningens navn", max_length=200)
    chairman = models.CharField("Formand", max_length=200, blank=True)
    chairman_email = models.EmailField("Formandens email", blank=True)
    second_chair = models.CharField("Næstformand", max_length=200, blank=True)
    second_chair_email = models.EmailField("Næstformandens email", blank=True)
    cashier = models.CharField("Kasserer", max_length=200, blank=True)
    cashier_email = models.EmailField("Kassererens email", blank=True)
    secretary = models.CharField("Sekretær", max_length=200, blank=True)
    secratary_email = models.EmailField("Sekretærens email", blank=True)
    union_email = models.EmailField("Foreningens email", blank=True)
    statues = models.URLField("Link til gældende vedtægter", blank=True)
    meeting_notes = models.URLField("Link til seneste referater", blank=True)
    founded = models.DateField("Stiftet", blank=True, null=True)
    regions = (("S", "Sjælland"), ("J", "Jylland"), ("F", "Fyn"), ("Ø", "Øer"))
    region = models.CharField("region", max_length=1, choices=regions)
    address = models.ForeignKey("Address", on_delete=models.PROTECT)
    boardMembers = models.TextField("Menige medlemmer", blank=True)
    bank_main_org = models.BooleanField(
        "Sæt kryds hvis I har konto hos hovedforeningen (og ikke har egen bankkonto).",
        default=True,
    )
    bank_account = models.CharField(
        "Bankkonto:",
        max_length=15,
        blank=True,
        help_text="Kontonummer i formatet 1234-1234567890",
        validators=[
            RegexValidator(
                regex="^[0-9]{4} *?-? *?[0-9]{6,10} *?$",
                message="Indtast kontonummer i det rigtige format.",
            )
        ],
    )

    def __str__(self):
        return "Foreningen for " + self.name

    def clean(self):
        if self.bank_main_org is False and not self.bank_account:
            raise ValidationError(
                "Vælg om foreningen har konto hos hovedforeningen. Hvis ikke skal bankkonto udfyldes."
            )

    def members(self):
        years = range(self.founded.year, (timezone.now().date.year) + 1)
        members = {}
        for year in years:
            temp_members = []
            union_activities_1 = Activity.objects.filter(
                member_justified=True,
                union=self.id,
                end_date__gt=F("start_date") + timedelta(days=2),
                start_date__year=year,
            )
            search_string = f"forenings medlemsskab {year}"
            union_activities_2 = Activity.objects.filter(
                member_justified=True, name__icontains=search_string
            ).union(union_activities_1)
            for activity in union_activities_2:
                for member in (
                    ActivityParticipant.objects.select_related("person")
                    .filter(activity=activity)
                    .distinct()
                ):
                    if (
                        len(
                            Payment.objects.filter(
                                person=members.person,
                                amount_ore__gte=7500,
                                activity=activity,
                                confirmed_dtm__lte=datetime(year, 9, 30),
                                refunded_dtm__isnull=True,
                            )
                        )
                        > 0
                    ):
                        temp_members.append(member.person)
            members[year] = temp_members
        return members

    def user_union_leader(self, user):
        if user.is_superuser:
            return True
        elif (
            # Remove False and #'s once "Foreningsledere fix" has been implemented.
            False
            # user == self.chairman.user
            # or user == self.second_chair.user
            # or user == self.cashier.user
            # or user == self.secretary.user
            # or self.board_members.objects.filter(Person__user=user) == user
        ):
            return True
        else:
            return False

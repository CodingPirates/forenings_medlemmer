#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.emailtemplate
import members.models.waitinglist
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone


# Calculate a day 14 days in the future
# TODO: make configurable in settings file
def _defaultInviteExpiretime():
    now = timezone.now()
    return now + timedelta(days=14)


class ActivityInvite(models.Model):
    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitationer"
        unique_together = ("activity", "person")

    activity = models.ForeignKey(
        "Activity", on_delete=models.DO_NOTHING, verbose_name="Aktivitet"
    )
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    invite_dtm = models.DateField("Inviteret", default=timezone.now)
    expire_dtm = models.DateField("Udløber", default=_defaultInviteExpiretime)
    rejected_at = models.DateField("Afslået", blank=True, null=True)
    help_price = (
        "Hvis det er et forløb / en sæsonaktivitet fratrækkes der automatisk 100 kr. "
    )
    help_price += (
        "til Coding Pirates Denmark pr. deltager. Denne pris overskriver prisen "
    )
    help_price += "på aktiviteten. Angiv kun en pris hvis denne deltager skal have en "
    help_price += (
        "anden pris end angivet i aktiviteten. Hvis prisen er under 100 kr. for "
    )
    help_price += (
        "et forløb / en sæsonaktivitet bliver barnet ikke medlem af foreningen "
    )
    help_price += (
        "og har ikke stemmeret til generalforsamlingen. Hvis der angives en anden "
    )
    help_price += (
        "pris, skal noten udfyldes med en begrundelse for denne prisoverskrivelse. "
    )
    help_price += "Denne note er synlig for den inviterede deltager."
    price_in_dkk = models.DecimalField(
        "Pris",
        max_digits=10,
        decimal_places=2,
        help_text=help_price,
        null=True,
        blank=True,
    )
    price_note = models.TextField("Note om særpris", blank=True)
    extra_email_info = models.TextField("Ekstra email info", blank=True)

    def clean(self):
        # Make sure we are not inviting outside activivty age limit
        if not (
            self.activity.start_date < timezone.now().date()
            or self.activity.min_age <= self.person.age_years() <= self.activity.max_age
        ):
            raise ValidationError(
                "Aktiviteten er kun for personer mellem "
                + str(self.activity.min_age)
                + " og "
                + str(self.activity.max_age)
                + " år"
            )

        if (
            self.price_in_dkk != self.activity.price_in_dkk
            and self.price_in_dkk is not None
            and self.price_note == ""
        ):
            raise ValidationError(
                "Du skal angive en begrundelse for den særlige pris for denne deltager. Noten er ikke synlig for deltageren."
            )

        errors = {}
        min_amount = self.activity.get_min_amount(self.activity.activitytype.id)

        if self.price_in_dkk is not None and self.price_in_dkk < min_amount:
            errors["price_in_dkk"] = (
                f"Prisen er for lav. Denne type aktivitet skal koste mindst {min_amount} kr."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Make sure price note is filled if there is a special price
        if self.price_in_dkk is None:
            self.price_in_dkk = self.activity.price_in_dkk

        if not self.id:
            super(ActivityInvite, self).save(*args, **kwargs)

            # Send out invitation email
            template = members.models.emailtemplate.EmailTemplate.objects.get(
                idname="ACT_INVITE"
            )

            context = {
                "activity": self.activity,
                "activity_invite": self,
                "person": self.person,
                "family": self.person.family,
                "email_extra_info": self.extra_email_info,
            }

            if self.person.email and (self.person.email != self.person.family.email):
                # If invited has own email, also send to that.
                template.makeEmail(
                    [self.person, self.person.family],
                    context,
                    True,
                )
            else:
                # otherwise use only family
                template.makeEmail(
                    self.person.family,
                    context,
                    True,
                )

            # remove from department waiting list
            if self.activity.is_season():
                members.models.waitinglist.WaitingList.objects.filter(
                    person=self.person, department=self.activity.department
                ).delete()
        return super(ActivityInvite, self).save(*args, **kwargs)

    def __str__(self):
        return "{}, {}".format(self.activity, self.person)

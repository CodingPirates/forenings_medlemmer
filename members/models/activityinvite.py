#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.emailtemplate
import members.models.waitinglist
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone


# Calculate a day 3 months in future
# TODO: make configurable in settings file
def _defaultInviteExpiretime():
    now = timezone.now()
    return now + timedelta(days=30 * 3)


class ActivityInvite(models.Model):
    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitationer"
        unique_together = ("activity", "person")

    activity = models.ForeignKey("Activity", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    invite_dtm = models.DateField("Inviteret", default=timezone.now)
    expire_dtm = models.DateField("Udløber", default=_defaultInviteExpiretime)
    rejected_dtm = models.DateField("Afslået", blank=True, null=True)

    def clean(self):
        # Make sure we are not inviting outside activivty age limit
        if not (
            self.activity.min_age <= self.person.age_years() <= self.activity.max_age
        ):
            raise ValidationError(
                "Aktiviteten er kun for personer mellem "
                + str(self.activity.min_age)
                + " og "
                + str(self.activity.max_age)
                + " år"
            )

    def save(self, *args, **kwargs):
        if not self.id:
            super(ActivityInvite, self).save(*args, **kwargs)
            template = members.models.emailtemplate.EmailTemplate.objects.get(
                idname="ACT_INVITE"
            )
            context = {
                "activity": self.activity,
                "activity_invite": self,
                "person": self.person,
                "family": self.person.family,
            }
            if self.person.email and (self.person.email != self.person.family.email):
                # If invited has own email, also send to that.
                template.makeEmail([self.person, self.person.family], context)
            else:
                # otherwise use only family
                template.makeEmail(self.person.family, context)
            # remove from department waiting list
            if self.activity.is_season():
                members.models.waitinglist.WaitingList.objects.filter(
                    person=self.person, department=self.activity.department
                ).delete()
        return super(ActivityInvite, self).save(*args, **kwargs)

    def __str__(self):
        return "{}, {}".format(self.activity, self.person)

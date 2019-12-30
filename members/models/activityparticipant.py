#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.payment
import members.models.member
import members.models.waitinglist
from django.utils import timezone


class ActivityParticipant(models.Model):
    class Meta:
        verbose_name = "Deltager"
        verbose_name_plural = "Deltagere"
        unique_together = ("activity", "member")

    added_dtm = models.DateField("Tilmeldt", default=timezone.now)
    activity = models.ForeignKey("Activity", on_delete=models.PROTECT)
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    note = models.TextField("Besked / Note til arrangement", blank=True)
    PHOTO_OK = "OK"
    PHOTO_NOTOK = "NO"
    PHOTO_PERMISSION_CHOICES = (
        (PHOTO_OK, "Tilladelse givet"),
        (PHOTO_NOTOK, "Ikke tilladt"),
    )
    photo_permission = models.CharField(
        "Foto tilladelse",
        max_length=2,
        choices=PHOTO_PERMISSION_CHOICES,
        default=PHOTO_NOTOK,
    )
    contact_visible = models.BooleanField(
        "Kontaktoplysninger synlige for andre holddeltagere", default=False
    )

    def __str__(self):
        return self.member.__str__() + ", " + self.activity.name

    def paid(self):
        # not paid if unconfirmed payments on this activity participation
        return not members.models.payment.Payment.objects.filter(
            activityparticipant=self, accepted_dtm=None
        )

    def get_payment_link(self):
        payment = members.models.payment.Payment.objects.get(
            activityparticipant=self, confirmed_dtm=None
        )
        if payment.payment_type == members.models.payment.Payment.CREDITCARD:
            return payment.get_quickpaytransaction().get_link_url()
        else:
            return 'javascript:alert("Kan ikke betales her:  Kontakt Coding Pirates for hjælp");'

    def save(self, *args, **kwargs):
        """ On creation if seasonal - clear all waiting lists """
        if not self.id:
            if self.activity.is_season():
                # remove from all waiting lists
                members.models.waitinglist.WaitingList.objects.filter(
                    person=self.member.person
                ).delete()
        return super(ActivityParticipant, self).save(*args, **kwargs)

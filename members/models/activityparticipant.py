#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.member
import members.models.waitinglist
import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


class ActivityParticipant(models.Model):
    class Meta:
        verbose_name = "Deltager"
        verbose_name_plural = "Deltagere"
        unique_together = ("activity", "member")

    payment = models.ForeignKey("Payment", on_delete=models.PROTECT, blank=True, null=True, default=None)
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
            confirmed_dtm=None, status="NEW"
        )

    def get_payment_link(self):
        payment = members.models.payment.Payment.objects.get(
            confirmed_dtm=None, status="NEW",
            activityparticipant__payment=self.payment
        )
        if payment.payment_type == members.models.payment.Payment.CREDITCARD:
            return payment.get_quickpaytransaction().get_link_url()
        else:
            return 'javascript:alert("Kan ikke betales her:  Kontakt Coding Pirates for hjælp");'

    def refundable(self):
        # if season, check if it's before 14 days after start
        # if it's not a season, check    that it's no later than 14 days after payment
        # and the activity_start date is before today.
        # also check that there doesn't exist a refund transaction
        payment = members.models.payment.Payment.objects.get(
            status="NEW", activityparticipant__payment=self.payment,
            confirmed_dtm__isnull=False)
        if payment:
            try:
                refund_check = members.models.payment.Payment.objects.get(
                    external_id=payment.external_id, status="REFUNDED",
                    confirmed_dtm__isnull=False
                )
            except ObjectDoesNotExist:
                # A payment has been made and no refund transaction exists
                # Check the dates
                season = members.models.activity.Activity.objects.get(
                    activityparticipant__activity=self.activity)
                if season.member_justified:
                    return (payment.confirmed_dtm.date() - season.start_date).days <= 14
                else:
                    return (payment.confirmed_dtm.date() - timezone.now().date()).days <= 14 and (season.start_date > timezone.now().date())
            return False

    def save(self, *args, **kwargs):
        """ On creation if seasonal - clear all waiting lists """
        if not self.id:
            if self.activity.is_season():
                # remove from all waiting lists
                members.models.waitinglist.WaitingList.objects.filter(
                    person=self.member.person
                ).delete()
        return super(ActivityParticipant, self).save(*args, **kwargs)

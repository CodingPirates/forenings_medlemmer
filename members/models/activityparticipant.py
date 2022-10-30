#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.payment
import members.models.member
import members.models.family
import members.models.person
import members.models.waitinglist
from django.utils import timezone
from django.utils.html import format_html


class ActivityParticipant(models.Model):
    class Meta:
        verbose_name = "Deltager"
        verbose_name_plural = "Deltagere"
        unique_together = ("activity", "member")

    added_dtm = models.DateField("Tilmeldt", default=timezone.now)
    activity = models.ForeignKey(
        "Activity", on_delete=models.PROTECT, verbose_name="Aktivitet"
    )
    member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, verbose_name="Medlem"
    )
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
        return self.member.__str__()
        # + ", " + self.activity.name
        # No reason to show an activity here - looks like it's the first activity for the given user

    def paid(self):
        # not paid if unconfirmed payments on this activity participation
        return not members.models.payment.Payment.objects.filter(
            activityparticipant=self, accepted_dtm=None
        )

    def payment_info(self, format_as_html: bool):
        ymdhm = "%Y-%m-%d %H:%M"
        payment = members.models.payment.Payment.objects.get(activityparticipant=self)
        if format_as_html:
            html_error_pre = "<span style='color:red'><b>"
            html_warn_pre = "<span style='color:blue'><b>"
            html_good_pre = "<span style='color:green'><b>"
            html_post = "</b></span>"
        else:
            html_error_pre = ""
            html_good_pre = ""
            html_warn_pre = ""
            html_post = ""

        result_string = "asdf"
        if payment.refunded_dtm is not None:
            result_string = f'{html_warn_pre}Refunderet{html_post}:{payment.refunded_dtm.strftime(ymdhm)}. '
            if payment.confirmed_dtm is not None:
                result_string += (
                    f'Betalt:{payment.confirmed_dtm.strftime(ymdhm)}. '
                )
            else:
                result_string += (
                    f'(Oprettet:{payment.added.strftime(ymdhm)})'
                )

        elif payment.rejected_dtm is not None:
            result_string = f'{html_error_pre}Afvist:{html_post}{payment.rejected_dtm.strftime(ymdhm)}. '
            result_string += f'(Oprettet:{payment.added.strftime(ymdhm)})'
        elif payment.cancelled_dtm is not None:
            result_string = f'{html_error_pre}Cancelled:{html_post}{payment.cancelled_dtm.strftime(ymdhm)}. '
            result_string += f'(Oprettet:{payment.added.strftime(ymdhm)})'
        else:
            if payment.confirmed_dtm is not None:
                result_string = f'{html_good_pre}Betalt:{html_post}{payment.confirmed_dtm.strftime(ymdhm)}. '
            else:
                result_string = f"{html_error_pre}IKKE BETALT.{html_post} "
            result_string += f'(Oprettet:{payment.added.strftime(ymdhm)})'

        if format_as_html:
            return format_html(result_string)
        else:
            return result_string

    def get_payment_link(self):
        payment = members.models.payment.Payment.objects.get(
            activityparticipant=self, confirmed_dtm=None
        )
        if payment.payment_type == members.models.payment.Payment.CREDITCARD:
            return payment.get_quickpaytransaction().get_link_url()
        else:
            return 'javascript:alert("Kan ikke betales her:  Kontakt Coding Pirates for hjælp");'

    def save(self, *args, **kwargs):
        """On creation if seasonal - clear all waiting lists"""
        if not self.id:
            if self.activity.is_season():
                # remove from all waiting lists
                members.models.waitinglist.WaitingList.objects.filter(
                    person=self.member.person
                ).delete()
        return super(ActivityParticipant, self).save(*args, **kwargs)

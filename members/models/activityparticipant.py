#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.payment
import members.models.family
import members.models.person
import members.models.waitinglist
import members.models.activity
import pytz
from django.utils import timezone
from django.utils.html import format_html


class ActivityParticipant(models.Model):
    class Meta:
        verbose_name = "Deltager"
        verbose_name_plural = "Deltagere"
        unique_together = ("activity", "person")

    added_at = models.DateField("Tilmeldt", default=timezone.now)
    activity = models.ForeignKey(
        "Activity", on_delete=models.PROTECT, verbose_name="Aktivitet"
    )
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, verbose_name="Person", null=True
    )
    note = models.TextField("Besked / Note til aktivitet", blank=True)
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

    def __str__(self):
        return (
            self.person.__str__()
            + ", "
            + self.activity.department.name
            + ", "
            + self.activity.name
        )

    def paid(self):
        # not paid if unconfirmed payments on this activity participation
        return not members.models.payment.Payment.objects.filter(
            activityparticipant=self, accepted_at=None
        )

    def payment_info_text(self):
        return self.payment_info(False)

    payment_info_text.short_description = "Betalingsinfo"

    def payment_info_html(self):
        return self.payment_info(True)

    payment_info_html.short_description = "Betalingsinfo"

    def payment_info(self, format_as_html: bool):
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

        result_string = ""

        # Checking for price = 0 before checking for payment
        if self.activity.price_in_dkk == 0:
            result_string = f"{html_good_pre}Gratis.{html_post} "
            if format_as_html:
                return format_html(result_string)
            else:
                return result_string

        try:
            payment = members.models.payment.Payment.objects.get(
                activityparticipant=self
            )
        except Exception:
            if format_as_html:
                result_string = format_html(
                    f"{html_error_pre}Andet er aftalt.{html_post} "
                )
            else:
                result_string = "Andet er aftalt. "
            return result_string

        paid_kr = f"{payment.amount_ore / 100:.2f}"
        if payment.refunded_at is not None:
            result_string += f"{html_warn_pre}Refunderet{html_post}:{self.utc_to_local_ymdhm(payment.refunded_at)}. "
            if payment.confirmed_at is not None:
                result_string += f"Betalt {paid_kr}kr: {self.utc_to_local_ymdhm(payment.confirmed_at)}. "
            else:
                result_string += (
                    f"(Oprettet:{self.utc_to_local_ymdhm(payment.added_at)})"
                )
        elif payment.rejected_at is not None:
            result_string += f"{html_error_pre}Afvist:{html_post}{self.utc_to_local_ymdhm(payment.rejected_at)}. "
            result_string += f"(Oprettet:{self.utc_to_local_ymdhm(payment.added_at)})"
        elif payment.cancelled_at is not None:
            result_string += f"{html_error_pre}Cancelled:{html_post}{self.utc_to_local_ymdhm(payment.cancelled_at)}. "
            result_string += f"(Oprettet:{self.utc_to_local_ymdhm(payment.added_at)})"
        else:
            if payment.confirmed_at is not None:
                result_string += f"{html_good_pre}Betalt {paid_kr}kr:{html_post} {self.utc_to_local_ymdhm(payment.confirmed_at)}. "
            else:
                if (
                    payment.accepted_at is not None
                    and self.activity.start_date.year > timezone.now().year
                ):
                    result_string += f"{html_warn_pre}Betalingsdato:{str(self.activity.start_date.year)}-01-01{html_post} "
                else:
                    result_string += (
                        f"{html_error_pre}Betaling er ikke gennemført{html_post} "
                    )

            result_string += f"(Oprettet:{self.utc_to_local_ymdhm(payment.added_at)})"
        if format_as_html:
            return format_html(result_string)
        else:
            return result_string

    def get_payment_link(self):
        payment = members.models.payment.Payment.objects.get(
            activityparticipant=self, confirmed_at=None
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
                    person=self.person
                ).delete()
        return super(ActivityParticipant, self).save(*args, **kwargs)

    @staticmethod
    def utc_to_local_ymdhm(timestamp_utc):
        ymdhm = "%Y-%m-%d %H:%M"
        utc = timestamp_utc.replace(tzinfo=pytz.UTC)
        local_time = utc.astimezone(timezone.get_current_timezone())
        return local_time.strftime(ymdhm)

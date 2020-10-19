#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.quickpaytransaction
from django.utils import timezone


class Payment(models.Model):
    CASH = "CA"
    BANKTRANSFER = "BA"
    CREDITCARD = "CC"
    REFUND = "RE"
    OTHER = "OT"
    PAYMENT_METHODS = (
        (CASH, "Kontant betaling"),
        (BANKTRANSFER, "Bankoverførsel"),
        (CREDITCARD, "Kreditkort"),
        (REFUND, "Refunderet"),
        (OTHER, "Andet"),
    )
    added = models.DateTimeField("Tilføjet", default=timezone.now)
    payment_type = models.CharField(
        "Type",
        blank=False,
        null=False,
        max_length=2,
        choices=PAYMENT_METHODS,
        default=CASH,
    )
    activity = models.ForeignKey(
        "Activity", blank=True, null=True, on_delete=models.PROTECT
    )
    activityparticipant = models.ForeignKey(
        "ActivityParticipant", blank=True, null=True, on_delete=models.PROTECT
    )  # unlink if failed and new try is made
    person = models.ForeignKey(
        "Person", blank=True, null=True, on_delete=models.PROTECT
    )
    family = models.ForeignKey(
        "Family", blank=False, null=False, on_delete=models.PROTECT
    )
    body_text = models.TextField("Beskrivelse", blank=False)
    amount_ore = models.IntegerField(
        "Beløb i øre", blank=False, null=False, default=0
    )  # payments to us is positive
    accepted_dtm = models.DateTimeField(
        "Accepteret", blank=True, null=True
    )  # Set when card data entered and amount reserved
    confirmed_dtm = models.DateTimeField(
        "Bekræftet", blank=True, null=True
    )  # Set when paid (and checked)
    cancelled_dtm = models.DateTimeField(
        "Annulleret", blank=True, null=True
    )  # Set when transaction is cancelled
    refunded_dtm = models.DateTimeField(
        "Refunderet", blank=True, null=True
    )  # Set when transaction is cancelled
    rejected_dtm = models.DateTimeField(
        "Afvist", blank=True, null=True
    )  # Set if paiment failed
    rejected_message = models.TextField(
        "Afvist årsag", blank=True, null=True
    )  # message describing failure

    def save(self, *args, **kwargs):
        is_new = (
            not self.pk
        )  # set when calling super, which is needed before we can link to this
        super_return = super(Payment, self).save(*args, **kwargs)

        """ On creation make quickpay transaction if paymenttype CREDITCARD """
        if is_new and self.payment_type == Payment.CREDITCARD:
            quickpay_transaction = (
                members.models.quickpaytransaction.QuickpayTransaction(
                    payment=self, amount_ore=self.amount_ore
                )
            )
            quickpay_transaction.save()
        return super_return

    def __str__(self):
        return str(self.family.email) + " - " + self.body_text

    def get_quickpaytransaction(self):
        return self.quickpaytransaction_set.order_by("-payment__added")[0]

    def set_accepted(self):
        if self.accepted_dtm is None:
            self.accepted_dtm = timezone.now()
            self.save()

    def set_confirmed(self):
        # Necessary if payment was autocaptured
        self.set_accepted()
        if self.confirmed_dtm is None:
            self.confirmed_dtm = timezone.now()
            self.rejected_dtm = None
            self.rejected_message = None
            self.save()

    def set_rejected(self, message):
        if self.rejected_dtm is None:
            self.confirmed_dtm = None
            self.rejected_dtm = timezone.now()
            self.rejected_message = message
            self.save()

    @staticmethod
    def capture_oustanding_payments():
        # get payments that are not confirmed and where activity starts this year
        payments = Payment.objects.filter(
            accepted_dtm__isnull=False,
            rejected_dtm__isnull=True,
            cancelled_dtm__isnull=True,
            confirmed_dtm__isnull=True,
            payment_type=Payment.CREDITCARD,
            added__lte=timezone.now(),
        )

        for payment in payments:
            payment.get_quickpaytransaction().capture()

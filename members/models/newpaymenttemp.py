#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.quickpaytransaction
from django.utils import timezone


class NewPaymentTemp(models.Model):
    CASH = "CA"
    BANKTRANSFER = "BA"
    CREDITCARD = "CC"
    REFUND = "RE"
    DEBIT = "DE"
    OTHER = "OT"
    PAYMENT_METHODS = (
        (CASH, "Kontant betaling"),
        (BANKTRANSFER, "Bankoverførsel"),
        (CREDITCARD, "Kreditkort"),
        (REFUND, "Refunderet"),
        (OTHER, "Andet"),
    )
    old_pk = models.IntegerField("Gammel primær nøgle", blank=True, null=True)
    added = models.DateTimeField("Tilføjet", default=timezone.now)
    payment_type = models.CharField(
        "Type",
        max_length=2,
        choices=PAYMENT_METHODS,
        default=CASH,
    )
    activityparticipant = models.ForeignKey(
        "ActivityParticipant", blank=True, null=True, on_delete=models.PROTECT
    )  # unlink if failed and new try is made
    person = models.ForeignKey(
        "Person", blank=True, null=True, on_delete=models.PROTECT
    )
    body_text = models.TextField("Beskrivelse", blank=False)
    amount_ore = models.IntegerField(
        "Beløb i øre", default=0
    )
    confirmed_dtm = models.DateTimeField(
        "Bekræftet", blank=True, null=True
    ) # Set when transaction is confirmed
    status = models.CharField(
        "Status",
        max_length=2,
        default=NEW,
        choices=(
                ("NEW", "Ny transaktion"),
                ("CANCELLED", "Annulleret"),
                ("REFUNDED", "Refunderet"),
        ),
    )
    rejected_dtm = models.DateTimeField(
        "Afvist", blank=True, null=True
    )
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
            quickpay_transaction = members.models.quickpaytransaction.QuickpayTransaction(
                payment=self, amount_ore=self.amount_ore
            )
            quickpay_transaction.save()
        return super_return

    def __str__(self):
        return str(self.family.email) + " - " + self.body_text

    def get_quickpaytransaction(self):
        return self.quickpaytransaction_set.order_by("-payment__added")[0]

    def set_confirmed(self):
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

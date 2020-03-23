from django.db import models
from django.core.mail import send_mail


class Email(models.Model):
    person = models.ForeignKey(
        "Person",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="recived_emails",
    )
    template = models.CharField("EmailTemplate", max_length=20)
    sent_dtm = models.DateTimeField("Sendt tidstempel", blank=True, null=True)

    def __str__(self):
        return f"{self.template} sendt til {self.person}"

    @staticmethod
    def send_payment_confirmation(payment):
        return send_mail(
            "Subject here",
            "here is the message",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django.utils.html import escape
import uuid


class EmailItem(models.Model):
    person = models.ForeignKey(
        "Person", blank=True, null=True, on_delete=models.CASCADE
    )
    family = models.ForeignKey(
        "Family", blank=True, null=True, on_delete=models.CASCADE
    )
    reciever = models.EmailField("Modtager", null=False)
    template = models.ForeignKey(
        "EmailTemplate", null=True, on_delete=models.DO_NOTHING
    )
    bounce_token = models.UUIDField(default=uuid.uuid4, null=False)
    activity = models.ForeignKey("Activity", null=True, on_delete=models.DO_NOTHING)
    department = models.ForeignKey(
        "Department", blank=True, null=True, on_delete=models.DO_NOTHING
    )

    created_dtm = models.DateTimeField("Oprettet", auto_now_add=True)
    subject = models.CharField("Emne", max_length=200, blank=True)
    body_html = models.TextField("HTML Indhold", blank=True)
    body_text = models.TextField("Text Indhold", blank=True)
    sent_dtm = models.DateTimeField("Sendt tidstempel", blank=True, null=True)
    send_error = models.CharField(
        "Fejl i afsendelse", max_length=200, blank=True, editable=False
    )

    def sent_ymdhm(self, format_as_html: bool):
        if self.sent_dtm is None:
            if format_as_html:
                msg = "&nbsp;"
            else:
                msg = ""
        else:
            msg = self.sent_dtm.strftime("%Y-%m-%d %H:%M ")
        if format_as_html:
            hoover_msg = "Oprettet: " + escape(
                self.created_dtm.strftime("%Y-%m-%d %H:%M")
            )

            return format_html(f'<div title=" {hoover_msg}">{msg}</div>')
        else:
            return msg

    sent_ymdhm.short_description = "Sendt"

    def sent_ymdhm_html(self):
        return self.sent_ymdhm(True)

    sent_ymdhm_html.short_description = "Sendt"

    def sent_ymdhm_text(self):
        return self.sent_ymdhm(False)

    sent_ymdhm_text.short_description = "Sendt"

    def subject_and_email(self, format_as_html: bool):
        if format_as_html:
            return format_html(
                f'<div title="{escape(self.body_html)}">{self.subject}</div>'.replace(
                    "{", ""
                ).replace("}", "")
            )
        else:
            return f"Subject:{self.subject}\nEmail:\n{self.body_text}"

    subject_and_email.short_description = "Emne og email"

    def subject_and_email_html(self):
        return self.subject_and_email(True)

    subject_and_email_html.short_description = "Emne og email"

    def subject_and_email_text(self):
        return self.subject_and_email(False)

    subject_and_email_text.short_description = "Emne og email"

    # send this email. Notice no checking of race condition, so this should be called by
    # cronscript and made sure the same mail is not sent multiple times in parallel
    def send(self):
        self.sent_dtm = timezone.now()
        self.save()
        try:
            send_mail(
                self.subject,
                self.body_text,
                settings.SITE_CONTACT,
                (self.reciever,),
                html_message=self.body_html,
            )
        except Exception as e:
            self.send_error = str(type(e))
            self.send_error = self.send_error + str(e)
            self.save()
            raise e  # forward exception to job control

        self.save()

    def __str__(self):
        return str(self.reciever) + " '" + self.subject + "'"

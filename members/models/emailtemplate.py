#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import members.models.emailitem
import members.models.person
import members.models.department
import members.models.family
from django.conf import settings
from django.template import Engine, Context


class EmailTemplate(models.Model):
    class Meta:
        verbose_name = "Email Skabelon"
        verbose_name_plural = "Email Skabeloner"

    idname = models.SlugField(
        "Unikt reference navn", max_length=50, blank=False, unique=True
    )
    updated_dtm = models.DateTimeField("Sidst redigeret", auto_now=True)
    name = models.CharField("Skabelon navn", max_length=200, blank=False)
    description = models.CharField("Skabelon beskrivelse", max_length=200, blank=False)
    template_help = models.TextField("Hjælp omkring template variable", blank=True)
    from_address = models.EmailField()
    subject = models.CharField("Emne", max_length=200, blank=False)
    body_html = models.TextField("HTML Indhold", blank=True)
    body_text = models.TextField("Text Indhold", blank=True)

    def __str__(self):
        return self.name + " (ID:" + self.idname + ")"

    # Will create and put an email in Queue from this template.
    # It will try to to put usefull details in context, which in many cases can just be {}

    # context is always filled with:
    #  email, site

    # If possible it will also be filled with:
    #  person, family

    # receivers are expected to be a list of Person, Family or strings (email adresses)

    def makeEmail(self, receivers, context, allow_multiple_emails=False):
        if type(receivers) is not list:
            receivers = [receivers]

        emails = []

        for receiver in receivers:
            # each receiver must be Person, Family or string (email)

            # Note - string specifically removed. We use family.dont_send_mails to make sure
            # we dont send unwanted mails.

            if type(receiver) not in (
                members.models.person.Person,
                members.models.family.Family,
                members.models.department.Department,
            ):
                raise Exception(
                    "Receiver must be of type Person or Family not "
                    + str(type(receiver))
                )

            # figure out receiver
            if type(receiver) is str:
                # check if family blacklisted. (TODO)
                destination_address = receiver
            elif type(receiver) is members.models.person.Person:
                # skip if family does not want email
                if receiver.family.dont_send_mails:
                    continue
                context["person"] = receiver
                destination_address = receiver.email
            elif type(receiver) is members.models.family.Family:
                # skip if family does not want email
                if receiver.dont_send_mails:
                    continue
                context["family"] = receiver
                destination_address = receiver.email
            elif type(receiver) is members.models.department.Department:
                context["department"] = receiver
                destination_address = receiver.department_email

            # figure out Person and Family is applicable
            if type(receiver) is members.models.person.Person:
                person = receiver
            elif "person" in context:
                person = context["person"]
            else:
                person = None

            # figure out family
            if type(receiver) is members.models.family.Family:
                family = receiver
            elif type(receiver) is members.models.person.Person:
                family = receiver.family
            elif "family" in context:
                family = context["family"]
            else:
                family = None

            # figure out activity
            if "activity" in context:
                activity = context["activity"]
            else:
                activity = None

            # department
            if "department" in context:
                department = context["department"]
            else:
                department = None

            # fill out known usefull stuff for context
            if "email" not in context:
                context["email"] = destination_address
            if "site" not in context:
                context["site"] = settings.BASE_URL
            if "person" not in context:
                context["person"] = person
            if "family" not in context:
                context["family"] = family

            # Make real context from dict
            context = Context(context)

            # render the template
            html_content = Engine.get_default().from_string(self.body_html)
            text_content = Engine.get_default().from_string(self.body_text)
            subject_content = Engine.get_default().from_string(self.subject)

            html_content = self.renderAndValidate(html_content, context)
            text_content = self.renderAndValidate(text_content, context)
            subject_content = self.renderAndValidate(subject_content, context)

            if (
                allow_multiple_emails
                or members.models.emailitem.EmailItem.objects.filter(
                    person=person,
                    receiver=destination_address,
                    activity=activity,
                    template=self,
                    department=department,
                ).count()
                < 1
            ):
                email = members.models.emailitem.EmailItem.objects.create(
                    template=self,
                    receiver=destination_address,
                    person=person,
                    family=family,
                    activity=activity,
                    department=department,
                    subject=subject_content,
                    body_html=html_content,
                    body_text=text_content,
                )
                email.save()
                emails.append(email)
        return emails

    def renderAndValidate(self, template, context):
        rendered = template.render(context)
        validated = rendered.replace("{", "").replace("}", "")

        return validated

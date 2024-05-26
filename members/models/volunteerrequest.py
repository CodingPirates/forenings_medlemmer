#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

class VolunteerRequest(models.Model):
    class Meta:
        verbose_name = "Frivillig anmodning"
        verbose_name_plural = "Frivillig anmodninger"

    person = models.ForeignKey("Person", blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField("Navn", max_length=200, blank=True )
    email = models.EmailField("Email", max_length=254, blank=True)
    phone = models.CharField("Telefon", max_length=50, blank=True)
    age = models.integer("Alder", blank=True)
    zip = models.CharField("Postnummer", max_length=4, blank=True)
    info_reference = models.TextField("Reference", max_length=200, help_text="Hvor har du hørt om Coding Pirates (SoMe, Facebook, Instagram, LinkedIn, en ven, en kollega, etc)")
    info_whishes = models.TextField("Ønsker", max_length=1024, help_text="Hvilke ønsker har du til at være frivillig hos Coding Pirates")
    created = models.DateTimeField(
        "Oprettet",
        blank = False,
        default=timezone.now,
        help_text = "Tidspunkt for oprettelse"
    )
    finished = models.DateTimeField(
        "Færdigbehandlet",
        blank = True,
        help_text = "Tidspunkt for færdigbehandling"
    )

    def __str__(self):
        return f"{self.name} <{self.email}> ({self.created.strftime("%Y-%m-%d %H:%M:%s")})"
    

    def save(self, *args, **kwargs):
        print("VolunteerRequest.Save()")
        print(f" pk:{self.pk} person:{self.person} name:{self.name}")
        print(f" email:{self.email}. phone:{self.phone}")
        super().save(*args, **kwargs)
        print(" saved")

        


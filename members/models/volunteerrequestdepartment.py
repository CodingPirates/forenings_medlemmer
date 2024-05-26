#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

class VolunteerRequestDepartment(models.Model):
    class Meta:
        verbose_name = "Frivillig anmodning for en afdeling"
        verbose_name_plural = "Frivillig anmodninger for afdelinger"
    
    volunteer_request = models.ForeignKey("VolunteerRequest", verbose_name="Frivillig Anmodning", on_delete=models.PROTECT)
    department = models.ForeignKey("Department", verbose_name = "Afdeling", on_delete=models.PROTECT)
    created = models.DateTimeField(
        "Oprettet",
        blank = False,
        default=timezone.now,
        help_text = "Tidspunkt for oprettelse"
    )
    finished = models.DateTimeField(
        "Færdigbehandlet",
        blank = True,
        null = True,
        help_text = "Tidspunkt for færdigbehandling"
    )

    STATUS_CHOICES = (
        (1, "Ny anmodning"),
        (2, "Afvist af afdeling"),
        (3, "Person er ikke interesseret"),
        (4, "Aktiv")
    )

    status = models.IntegerField("Status", choices = STATUS_CHOICES, default = 1)

 
    def __str__(self):
        return f"{self.department}: {self.volunteer_request}"


    def save(self, *args, **kwargs):
        print("VolunteerRequestDepartment.Save")
        print(f" V.req:{self.volunteer_request}. Dep:{self.department}")
        super().save(*args, **kwargs)
        

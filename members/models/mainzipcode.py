from django.db import models
from django.urls import reverse

class MainZipcode(models.Model):
    class Meta:
        verbose_name = "Hovedpostnummer"
        verbose_name_plural = "Hovedpostnumre"
    municipality = models.CharField("Kommune", max_length=100, blank=True, null=True)
    zipcode = models.CharField("Postnummer", max_length=4, blank=True)

from django.db import models


class Municipality(models.Model):
    name = models.CharField(max_length=255, verbose_name="Navn", default="")
    address = models.CharField(max_length=255, verbose_name="Adresse")
    zipcode = models.CharField(max_length=10, verbose_name="Postnr")
    city = models.CharField(max_length=100, verbose_name="By")
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)

    def __str__(self):
        return f"{self.name}, {self.zipcode} {self.city}"

    class Meta:
        verbose_name = "Kommune"
        verbose_name_plural = "Kommuner"
        ordering = ["name"]

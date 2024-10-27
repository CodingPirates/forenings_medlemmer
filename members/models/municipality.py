from django.db import models


class Municipality(models.Model):
    municipality = models.CharField(max_length=255, verbose_name="Kommune")
    address = models.CharField(max_length=255, verbose_name="Adresse")
    zipcode = models.CharField(max_length=10, verbose_name="Postnr")
    city = models.CharField(max_length=100, verbose_name="By")
    email = models.EmailField(verbose_name="E-mail")

    def __str__(self):
        return f"{self.municipality}, {self.zipcode} {self.city}"

    class Meta:
        verbose_name = "Kommune"
        verbose_name_plural = "Kommuner"
        ordering = ["municipality"]

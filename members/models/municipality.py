from django.db import models
import requests


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

    @staticmethod
    def get_municipality_for_person(person) -> bool:
        # Call the API to get municipality id
        url = f"https://api.dataforsyningen.dk/adresser?id={person.dawa_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if not data:
                return False

            municipality_id = data[0]["adgangsadresse"]["kommune"]["kode"]

            if municipality_id:
                try:
                    # Look up the found municipality id from Municipality model
                    municipality = Municipality.objects.get(dawa_id=municipality_id)
                    # Set the municipality for the person
                    person.municipality = municipality
                    person.save()
                    return True
                except Municipality.DoesNotExist:
                    return False

        return False

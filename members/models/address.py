from django.db import models
import requests

from members.models import Department


class Address(models.Model):
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresser"
        ordering = ["zipcode"]

    streetname = models.CharField("Vejnavn", max_length=200)
    housenumber = models.CharField("Husnummer", max_length=5)
    floor = models.CharField("Etage", max_length=10, blank=True, null=True)
    door = models.CharField("Dør", max_length=10, blank=True, null=True)
    city = models.CharField("By", max_length=200)
    zipcode = models.CharField("Postnummer", max_length=4)
    municipality = models.CharField("Kommune", max_length=100, blank=True, null=True)
    longitude = models.DecimalField(
        "Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        "Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)

    def __str__(self):
        address = f"{self.streetname} {self.housenumber}"
        address = f"{address} {self.floor}" if self.floor is not None else address
        address = f"{address} {self.door}" if self.door is not None else address
        return f"{address}, {self.zipcode} {self.city}"

    def save(self, *args, **kwargs):
        if self._state.adding and self.longitude is None:  # On first save with no data
            self.get_dawa_data()
        super().save(*args, **kwargs)

    def get_dawa_data(self):
        if self.dawa_id == "":
            wash_resp = requests.request(
                "GET",
                "https://dawa.aws.dk/datavask/adresser",
                params={"betegnelse": str(self)},
            )
            if wash_resp.status_code != 200 or wash_resp.json()["kategori"] == "C":
                return False
            else:
                self.dawa_id = wash_resp.json()["resultater"][0]["adresse"]["id"]

        data_resp = requests.request(
            "GET",
            f"https://dawa.aws.dk/adresser/{self.dawa_id}",
            params={"format": "geojson"},
        )
        if data_resp.status_code != 200:
            self.dawa_id = ""
            return False

        dawa_data = data_resp.json()["properties"]
        self.streetname = dawa_data["vejnavn"]
        self.housenumber = dawa_data["husnr"]
        self.floor = dawa_data["etage"]
        self.door = dawa_data["dør"]
        self.city = dawa_data["postnrnavn"]
        self.zipcode = dawa_data["postnr"]
        self.municipality = dawa_data["kommunenavn"]
        self.longitude = dawa_data["wgs84koordinat_længde"]
        self.latitude = dawa_data["wgs84koordinat_bredde"]
        return True

    @staticmethod
    def get_by_dawa_id(dawa_id):
        addresses = Address.objects.filter(dawa_id=dawa_id)
        if len(addresses) > 0:
            return addresses[0]
        else:
            address = Address(dawa_id=dawa_id)
            if address.get_dawa_data():
                address.save()
                return address
            else:
                return None

    @staticmethod
    def get_user_addresses(user):
        if user.is_superuser:
            return Address.objects.all()
        address_ids = [
            department.address.id
            for department in Department.objects.filter(
                adminuserinformation__user=user
            ).exclude(address=None)
        ]
        return Address.objects.filter(pk__in=address_ids)

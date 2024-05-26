import requests

from django.db import models
from django.conf import settings

from .department import Department
from .union import Union
from .activity import Activity


class Address(models.Model):
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresser"
        ordering = ["zipcode"]

    streetname = models.CharField("Vejnavn", max_length=200)
    housenumber = models.CharField("Husnummer", max_length=5)
    floor = models.CharField("Etage", max_length=10, blank=True)
    door = models.CharField("Dør", max_length=10, blank=True)
    placename = models.CharField("Stednavn", max_length=200, blank=True)
    city = models.CharField("By", max_length=200)
    zipcode = models.CharField("Postnummer", max_length=4)
    REGION_CHOICES = (
        ("Region Syddanmark", "Syddanmark"),
        ("Region Hovedstaden", "Hovedstaden"),
        ("Region Nordjylland", "Nordjylland"),
        ("Region Midtjylland", "Midtjylland"),
        ("Region Sjælland", "Sjælland"),
        ("Online", "Online"),
        ("Andet", "Andet"),
    )
    region = models.CharField("Region", choices=REGION_CHOICES, max_length=20)
    municipality = models.CharField("Kommune", max_length=100, blank=True)
    longitude = models.DecimalField(
        "Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        "Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    help_temp = """
    Lader dig gemme en anden længde- og breddegrad end oplyst fra DAWA \
    (hvor vi henter adressedata). \
    Spørg os i #medlemsssystem_support på Slack hvis du mangler hjælp.
    """
    dawa_overwrite = models.BooleanField(
        "Overskriv DAWA", default=False, help_text=help_temp
    )
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)
    dawa_category = models.CharField("DAWA kategori", max_length=1, blank=True)
    created_at = models.DateTimeField(
        "Oprettet", auto_now=False, auto_now_add=True, auto_created=True
    )
    created_by = models.PositiveIntegerField("Oprettet af", default=0)
    descriptiontext = models.CharField("Beskrivelse", max_length=100, blank=True)

    def __str__(self):
        address = f"{self.streetname} {self.housenumber}"
        address = f"{address} {self.floor}" if self.floor != "" else address
        address = f"{address} {self.door}" if self.door != "" else address
        address = f"{address}, {self.placename}" if self.placename != "" else address
        return f"{address}, {self.zipcode} {self.city}"

    def save(self, *args, **kwargs):
        if settings.USE_DAWA_ON_SAVE and not self.dawa_overwrite:
            self.get_dawa_data()
        super().save(*args, **kwargs)

    def get_dawa_data(self):
        if self.dawa_id == "":
            wash_resp = requests.request(
                "GET",
                "https://dawa.aws.dk/datavask/adresser",
                params={"betegnelse": str(self)},
            )
            _category = wash_resp.json()["kategori"]
            # DAWA category "C" means that it was a low probability address match
            if wash_resp.status_code != 200 or _category == "C":
                return False
            else:
                self.dawa_id = wash_resp.json()["resultater"][0]["adresse"]["id"]
                self.dawa_category = _category

        data_resp = requests.request(
            "GET",
            f"https://dawa.aws.dk/adresser/{self.dawa_id}",
            params={"format": "geojson"},
        )
        if data_resp.status_code != 200:
            self.dawa_id = ""
            return False

        dawa_data = data_resp.json()["properties"]
        for key in dawa_data.keys():
            dawa_data[key] = "" if dawa_data[key] is None else dawa_data[key]
        self.streetname = dawa_data["vejnavn"]
        self.housenumber = dawa_data["husnr"]
        self.floor = dawa_data["etage"]
        self.door = dawa_data["dør"]
        self.placename = dawa_data["supplerendebynavn"]
        self.city = dawa_data["postnrnavn"]
        self.zipcode = dawa_data["postnr"]
        self.municipality = dawa_data["kommunenavn"]
        self.longitude = dawa_data["wgs84koordinat_længde"]
        self.latitude = dawa_data["wgs84koordinat_bredde"]
        self.region = dawa_data["regionsnavn"]
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
        if user.is_superuser or user.has_perm("members.view_all_departments"):
            return Address.objects.all()
        if user.has_perm("members.view_all_departments"):
            department_address_id = [
                department.address.id for department in Department.objects.all()
            ]
            department_id = [department.id for department in Department.objects.all()]
        else:
            department_address_id = [
                department.address.id
                for department in Department.objects.filter(
                    adminuserinformation__user=user
                )
            ]
            department_id = [
                department.id
                for department in Department.objects.filter(
                    adminuserinformation__user=user
                )
            ]

        if user.has_perm("members.view_all_unions"):
            union_address_id = [union.address.id for union in Union.objects.all()]
        else:
            union_address_id = [
                union.address.id
                for union in Union.objects.filter(adminuserinformation__user=user)
            ]

        activity_address_id = []
        for department in department_id:
            for activity in Activity.objects.filter(department_id=department):
                activity_address_id += [activity.address.id]

        # Find all addresses not used by Union nor Department nor Activity
        address_id_all = [address.id for address in Address.objects.all()]

        department_address_id_all = [
            department.address.id for department in Department.objects.all()
        ]
        union_address_id_all = [union.address.id for union in Union.objects.all()]
        activity_address_id_all = [
            activity.address.id for activity in Activity.objects.all()
        ]

        address_unused_ids = list(
            set(address_id_all)
            - set(department_address_id_all)
            - set(union_address_id_all)
            - set(activity_address_id_all)
        )
        address_ids = (
            address_unused_ids
            + department_address_id
            + union_address_id
            + activity_address_id
        )
        return Address.objects.filter(pk__in=address_ids)

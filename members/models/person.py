import random
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from members.models.municipality import Municipality
from django.core.exceptions import PermissionDenied, ValidationError
from members.utils.address import format_address
from urllib.parse import quote_plus
import requests
import logging

logger = logging.getLogger(__name__)


class Person(models.Model):
    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Personer"
        ordering = ["added_at"]
        permissions = (
            (
                "view_full_address",
                "Can view persons full address + phonenumber + email",
            ),
            (
                "view_all_persons",
                "Can view persons not related to department",
            ),
            (
                "anonymize_persons",
                "Can anonymize persons",
            ),
        )

    PARENT = "PA"
    GUARDIAN = "GU"
    CHILD = "CH"
    OTHER = "NA"
    MEMBER_TYPE_CHOICES = (
        (PARENT, "Forælder"),
        (GUARDIAN, "Værge"),
        (CHILD, "Barn"),
        (OTHER, "Andet"),
    )
    MALE = "MA"
    FEMALE = "FM"
    OTHER_GENDER = "OT"
    SELECT_GENDER_TEXT = "(Vælg køn)"
    MEMBER_GENDER_CHOICES = (
        ("", SELECT_GENDER_TEXT),
        (MALE, "Dreng"),
        (FEMALE, "Pige"),
        (OTHER_GENDER, "Andet"),
    )
    MEMBER_ADULT_GENDER_CHOICES = (
        ("", SELECT_GENDER_TEXT),
        (MALE, "Mand"),
        (FEMALE, "Kvinde"),
        (OTHER_GENDER, "Andet"),
    )
    membertype = models.CharField(
        "Type", max_length=2, choices=MEMBER_TYPE_CHOICES, default=PARENT
    )
    name = models.CharField(
        "Navn",
        max_length=200,
        validators=[
            RegexValidator(
                '^(?!.*[:;,"[\]{}*&^%$#@!_+=\/\\\\<>|])\S+\s+\S+.*$',  # noqa: W605
                message="Indtast et gyldigt navn bestående af fornavn og minimum et efternavn.",
            )
        ],
    )
    zipcode = models.CharField("Postnummer", max_length=4, blank=True)
    city = models.CharField("By", max_length=200, blank=True)
    streetname = models.CharField("Vejnavn", max_length=200, blank=True)
    housenumber = models.CharField("Husnummer", max_length=5, blank=True)
    floor = models.CharField("Etage", max_length=10, blank=True)
    door = models.CharField("Dør", max_length=5, blank=True)
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,  # allow blank/null values since we don't have addresses for all persons
        default="",
    )
    longitude = models.DecimalField(
        "Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        "Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)
    placename = models.CharField("Stednavn", max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField("Telefon", max_length=50, blank=True)
    gender = models.CharField(
        "Køn", max_length=20, choices=MEMBER_GENDER_CHOICES, default=None, null=True
    )
    birthday = models.DateField("Fødselsdag", blank=True, null=True)
    has_certificate = models.DateField("Børneattest", blank=True, null=True)
    family = models.ForeignKey("Family", on_delete=models.CASCADE)
    notes = models.TextField("Noter", blank=True, null=False, default="")
    added_at = models.DateTimeField("Tilføjet", default=timezone.now, blank=False)
    deleted_dtm = models.DateTimeField("Slettet", null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_DEFAULT,
        blank=True,
        null=True,
        default=None,
    )
    address_invalid = models.BooleanField("Ugyldig adresse", default=False)
    anonymized = models.BooleanField("Anonymiseret", default=False)

    def __str__(self):
        return self.name

    def address(self):
        return format_address(self.streetname, self.housenumber, self.floor, self.door)

    def addressWithZip(self):
        return self.address() + ", " + self.zipcode + " " + self.city

    def age_from_birthdate(self, date):
        today = timezone.now().date()
        return (
            today.year - date.year - ((today.month, today.day) < (date.month, date.day))
        )

    def age_years(self):
        if self.birthday is not None:
            return self.age_from_birthdate(self.birthday)
        else:
            return 0

    age_years.admin_order_field = "-birthday"
    age_years.short_description = "Alder"

    def firstname(self):
        return self.name.partition(" ")[0]

    def gender_text(self):
        if self.gender == self.MALE:
            return "Dreng/Mand"
        elif self.gender == self.FEMALE:
            return "Pige/Kvinde"
        elif self.gender == self.OTHER_GENDER:
            return "Andet"
        else:
            return "N/A"

    def update_dawa_data(self):
        if self.address_invalid:
            return None
        if (
            self.dawa_id is None
            or self.latitude is None
            or self.longitude is None
            or self.municipality is None
        ):
            try:
                url = f"https://api.dataforsyningen.dk/adresser?q={quote_plus(self.addressWithZip())}"
                response = requests.get(url)
                if response.status_code != 200:
                    self.address_invalid = True
                    self.save()
                    return None

                data = response.json()
                if not data:
                    self.address_invalid = True
                    self.save()
                    return None

                # DAWA returns result with address and "adgangsadresse". Address has fields "etage" and "dør",
                # whereas "adgangsadresse" has all the shared address fields (e.g. for an apartment building)
                address = data[0]
                access_address = address["adgangsadresse"]

                if address["etage"] is None:
                    address["etage"] = ""
                if address["dør"] is None:
                    address["dør"] = ""
                if access_address["supplerendebynavn"] is None:
                    access_address["supplerendebynavn"] = ""

                self.zipcode = access_address["postnummer"]["nr"]
                self.city = access_address["postnummer"]["navn"]
                self.streetname = access_address["vejstykke"]["navn"]
                self.housenumber = access_address["husnr"]
                self.floor = address["etage"]
                self.door = address["dør"]
                self.placename = access_address["supplerendebynavn"]
                self.latitude = access_address["vejpunkt"]["koordinater"][1]
                self.longitude = access_address["vejpunkt"]["koordinater"][0]
                self.municipality = Municipality.objects.get(
                    dawa_id=access_address["kommune"]["kode"]
                )
                self.dawa_id = address["id"]
                self.save()

            except Exception:
                self.address_invalid = True
                self.save()

    # TODO: Move to dawa_data in utils

    def anonymize(self, request):
        if not request.user.has_perm("members.anonymize_persons"):
            raise PermissionDenied(
                "Du har ikke tilladelse til at anonymisere personer."
            )

        if self.anonymized:
            raise ValidationError("Personen er allerede anonymiseret.")

        orig_email = self.email

        self.name = "Anonymiseret"
        self.zipcode = ""
        self.city = ""
        self.streetname = ""
        self.housenumber = ""
        self.floor = ""
        self.door = ""
        self.dawa_id = ""
        self.longitude = None
        self.latitude = None
        self.placename = ""
        self.email = ""
        self.phone = ""

        if self.birthday:
            original_birthday = self.birthday

            # Make sure we don't end up with the same birthday
            while self.birthday == original_birthday:
                self.birthday = self.birthday.replace(day=random.randint(1, 28))

        self.notes = ""
        self.address_invalid = (
            True  # don't try to update address for anonymized persons
        )
        self.anonymized = True
        self.save()

        # Remove person from all waiting lists
        for waiting_list in self.waitinglist_set.all():
            waiting_list.delete()

        self.family.anonymize_if_all_persons_anonymized(request)

        # anonymize sent emails
        email_items = self.emailitem_set.all()
        for email_item in email_items:
            email_item.subject = "Anonymiseret"
            email_item.body_text = ""
            email_item.body_html = ""
            email_item.receiver = ""
            email_item.save()

        # anonymize Django user if exists, there might be multiple users with the same email address
        users = User.objects.filter(email__exact=orig_email)
        if users.exists():
            for user in users:
                user.username = f"anonymized-{user.id}"
                user.first_name = "Anonymiseret"
                user.last_name = ""
                user.email = f"{user.username}@localhost"
                user.is_superuser = False
                user.is_staff = False
                user.is_active = False
                user.save()
        else:
            pass  # no user accounts found for this person

    firstname.admin_order_field = "name"
    firstname.short_description = "Fornavn"

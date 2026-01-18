import random
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from members.models.municipality import Municipality
from members.models.consent import Consent
from django.core.exceptions import PermissionDenied, ValidationError
from members.models.payment import Payment
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
            (
                "view_consent_information",
                "Can view consent information for persons",
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
                r'^(?!.*[:;,"[\]{}*&^%$#@!_+=\/\\\\<>|])\S+\s+\S+.*$',  # noqa: W605
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
        related_name="person_user",
    )
    address_invalid = models.BooleanField("Ugyldig adresse", default=False)
    anonymized = models.BooleanField("Anonymiseret", default=False)
    consent = models.ForeignKey(
        Consent, null=True, blank=True, on_delete=models.PROTECT
    )
    consent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_DEFAULT,
        blank=True,
        null=True,
        default=None,
        related_name="person_consent_by",
        verbose_name="Samtykke givet af",
    )
    consent_at = models.DateTimeField("Samtykke dato", null=True, blank=True)
    REGION_CHOICES = (
        ("Region Syddanmark", "Syddanmark"),
        ("Region Hovedstaden", "Hovedstaden"),
        ("Region Nordjylland", "Nordjylland"),
        ("Region Midtjylland", "Midtjylland"),
        ("Region Sjælland", "Sjælland"),
        ("Andet", "Andet"),
    )
    region = models.CharField(
        "Region",
        choices=REGION_CHOICES,
        max_length=20,
        blank=True,
        null=True,
        default=None,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not settings.TESTING:
            updated = self.update_dawa_data(force=True, save=False)
            if updated is not None:
                self = updated
        return super().save(*args, **kwargs)

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

    def is_anonymization_candidate(self, relaxed=False):
        """
        Determine if person is a candidate for anonymization.
        We cannot anonymize if there is a payment in the last 5 full fiscal years.

        Args:
            relaxed: If True, only checks for financial transactions. Allows anonymization
                    even if person has been logged in or created recently.

        Returns: Tuple (is_candidate, reason):
        - is_candidate: False if e.g. latest_activity
        - reason: Description of why the person is not a candidate
        """

        # we operate with two date boundaries:
        # - 2 years for login or participation in activities
        two_years_ago = timezone.now() - timedelta(days=2 * 365)

        # - January 1st of the year before 5 years ago, i.e. at least 5 full years,
        # for financial transactions
        #
        # current date 2025-09-27 => 2020-01-01
        today = timezone.now().date()
        five_full_fiscal_years = timezone.make_aware(datetime(today.year - 5, 1, 1))

        # If person has participated in activities within the last 2 years, then cannot be anonymized
        # Import here to avoid circular imports
        from .activityparticipant import ActivityParticipant

        latest_participation = (
            ActivityParticipant.objects.filter(person=self)
            .select_related("activity")
            .order_by("-activity__end_date")
            .first()
        )

        if latest_participation and latest_participation.activity.end_date:
            if latest_participation.activity.end_date >= two_years_ago.date():
                return False, "Har deltaget i aktiviteter seneste 2 år."

        # if in relaxed mode, we allow aononymization of persons created or logged in
        if not relaxed:
            if self.added_at >= two_years_ago:
                return False, "Oprettet indenfor seneste 2 år."

            if (
                self.user
                and self.user.last_login
                and self.user.last_login >= two_years_ago
            ):
                return False, "Har logget ind seneste 2 år."

        # We verify both person and family, i.e. a parent cannot be anonymized if there are payments for any of the children in family
        if (
            Payment.objects.filter(
                person=self, added_at__gte=five_full_fiscal_years
            ).exists()
            or Payment.objects.filter(
                family=self.family, added_at__gte=five_full_fiscal_years
            ).exists()
        ):
            return (
                False,
                "Der eksisterer betaling indenfor seneste 5 fulde regnskabsår.",
            )

        # otherwise, the person can be anonymized
        return True, ""

    def update_dawa_data(self, force=False, save=True):
        if self.address_invalid and not force:
            return None
        if (
            self.dawa_id is None
            or self.latitude is None
            or self.longitude is None
            or self.municipality is None
            or force
        ):
            try:
                url = f"https://api.dataforsyningen.dk/adresser?q={quote_plus(self.addressWithZip())}"
                response = requests.get(url)
                if response.status_code != 200:
                    self.address_invalid = True
                    if save:
                        self.save()
                    return self

                data = response.json()
                if not data:
                    self.address_invalid = True
                    if save:
                        self.save()
                    return self

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
                self.region = access_address["region"]["navn"]
                self.dawa_id = address["id"]
                if save:
                    self.save()
                return self

            except Exception:
                self.address_invalid = True
                if save:
                    self.save()

    # TODO: Move to dawa_data in utils

    def anonymize(self, request, relaxed=False):
        """
        Anonymize a person.

        Args:
            request: Request object with user that has anonymize_persons permission
            relaxed: If True, uses relaxed validation (only checks financial transactions).
                    Allows anonymization even if person has been logged in or created recently.
        """
        if not request.user.has_perm("members.anonymize_persons"):
            raise PermissionDenied(
                "Du har ikke tilladelse til at anonymisere personer."
            )

        if self.anonymized:
            raise ValidationError("Personen er allerede anonymiseret.")

        is_anonymization_candidate, reason = self.is_anonymization_candidate(
            relaxed=relaxed
        )
        if not is_anonymization_candidate:
            raise ValidationError(
                f"Personen {self.name} kan ikke anonymiseres: {reason}"
            )

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

        # anonymize activity participation notes
        activity_items = self.activityparticipant_set.all()
        for activity_item in activity_items:
            activity_item.note = ""
            activity_item.save()

        # anonymize Django user if exists
        try:
            user = User.objects.get(pk=self.user.pk)
            user.username = f"anonymized-{user.id}"
            user.first_name = "Anonymiseret"
            user.last_name = ""
            user.email = f"anonymized-{user.id}@localhost"
            user.is_superuser = False
            user.is_staff = False
            user.is_active = False
            user.save()
        except User.DoesNotExist:
            pass  # no user account found for this person, nothing to update then

    firstname.admin_order_field = "name"
    firstname.short_description = "Fornavn"

import uuid
from django.db import models
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .person import Person
import members.models.emailtemplate


class Family(models.Model):
    class Meta:
        verbose_name = "Familie"
        verbose_name_plural = "Familier"
        permissions = (
            (
                "view_family_unique",
                "Can view family UUID field (password) - gives access to address",
            ),
        )

    unique = models.UUIDField(default=uuid.uuid4, unique=True)
    email = models.EmailField(unique=True)
    dont_send_mails = models.BooleanField("Vil ikke kontaktes", default=False)
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)
    confirmed_at = models.DateTimeField("Bekræftet", null=True, blank=True)
    last_visit_dtm = models.DateTimeField("Sidst besøgt", null=True, blank=True)
    deleted_dtm = models.DateTimeField("Slettet", null=True, blank=True)
    anonymized = models.BooleanField("Anonymiseret", default=False)

    def get_abosolute_url(self):
        return reverse("family_form")

    def __str__(self):
        return self.email

    def send_link_email(self):
        members.models.emailtemplate.EmailTemplate.objects.get(idname="LINK").makeEmail(
            self, {}
        )

    def get_first_parent(self):
        try:
            parent = self.person_set.filter(
                membertype__in=(
                    Person.PARENT,
                    Person.GUARDIAN,
                )
            )[0]
        except IndexError:
            return None
        return parent

    def get_children(self):
        return Person.objects.filter(family=self, membertype=Person.CHILD)

    def get_persons(self):
        return Person.objects.filter(family=self)

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super(Family, self).save(*args, **kwargs)

    def anonymize(self, request):
        if not request.user.has_perm("members.anonymize_persons"):
            raise PermissionDenied(
                "Du har ikke tilladelse til at anonymisere personer eller familier."
            )

        non_anonymized_persons_in_family = self.person_set.filter(anonymized=False)
        if non_anonymized_persons_in_family.count() != 0:
            raise Exception(
                "Alle personer i en familie skal være anonymiseret, for at familien kan anonymiseres."
            )

        self.email = f"anonym-{self.id}@codingpirates.dk"
        self.dont_send_mails = True
        self.anonymized = True
        self.save()

    def anonymize_if_all_persons_anonymized(self, request):
        if not request.user.has_perm("members.anonymize_persons"):
            raise PermissionDenied(
                "Du har ikke tilladelse til at anonymisere personer eller familier."
            )

        non_anonymized_persons_in_family = self.person_set.filter(anonymized=False)
        if non_anonymized_persons_in_family.count() == 0:
            self.anonymize(request)

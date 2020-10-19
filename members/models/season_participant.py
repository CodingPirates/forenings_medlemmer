from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .waitinglist import WaitingList


class SeasonParticipant(models.Model):
    class Meta:
        verbose_name = "Sæsondeltager"
        verbose_name_plural = "Sæsondeltagere"
        unique_together = ("season", "person")

    sign_up_date = models.DateField("Tilmeldt", default=timezone.now)
    season = models.ForeignKey("Season", on_delete=models.PROTECT)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    note = models.TextField("Besked / Note til kaptajnen", blank=True)
    photo_permission = models.BooleanField("Foto tilladelse",)

    def clean(self):
        self.can_join_validator(self.season, self.person)

    def save(self, *args, **kwargs):
        self.clean()
        is_on_wait_list = WaitingList.objects.get(
            person=self.Person, department=self.department
        )
        if is_on_wait_list is not None:
            is_on_wait_list.delete()
        return super(SeasonParticipant, self).save(*args, **kwargs)

    @staticmethod
    def can_join_validator(season, person):
        if SeasonParticipant.objects.get(season=season, person=person) is not None:
            # Is already participant
            return

        if (
            SeasonParticipant.objects.filter(season=season).count()
            > season.max_participants
        ):
            raise ValidationError(
                f"{season} har fyldt alle sine {season.max_participants} pladser"
            )

        if person.age_years() < season.min_age or person.age_years() > season.max_age:
            raise ValidationError(
                f"{person} har en alder på {person.age_years()}, {season} har\
                alderskrav {season.min_age}:{season.max_age}"
            )
        if season.signup_closing < timezone.now():
            raise ValidationError(f"Tilmeldingen lukkede den {season.signup_closing}")

        if season.end_date < timezone.now():
            raise ValidationError(f"{season} sluttede den {season.end_date}")

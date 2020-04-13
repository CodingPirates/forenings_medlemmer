from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from .season_participant import SeasonParticipant


class SeasonInvite(models.Model):
    class Meta:
        verbose_name = "Sæsoninvitation"
        verbose_name_plural = "Sæsoninvitationer"
        unique_together = ("season", "person")

    season = models.ForeignKey("Season", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    invite_date = models.DateField("Inviteret", default=timezone.now)
    rejected_date = models.DateField("Afslået", blank=True, null=True)

    def clean(self):
        if timezone.now() > self.expire_date:
            raise ValidationError(f"Invitation er udløbet")

        SeasonParticipant.can_join_validator(self.person, self.person)

    def save(self, *args, **kwargs):
        # TODO Send email with invite and add remove from waiting list button
        # To email
        return super(SeasonInvite, self).save(*args, **kwargs)

    def __str__(self):
        return "{}, {}".format(self.activity, self.person)

# Added to support different types of activities.
# Makes is possible to filter certain activities out when showing the list to users.

from django.db import models
from django.utils import timezone


class ActivityType(models.Model):
    class Meta:
        verbose_name = "Aktivitetstype"
        verbose_name_plural = "Aktivitetstype"
        ordering = ["name"]

    name = models.CharField(
        "Aktivitetstype",
        max_length=50,
        help_text="Kort beskrivelse af aktivitetstype. Fx 'Støttemedlem'.",
    )
    description = models.CharField(
        "Beskrivelse",
        max_length=200,
        help_text="Uddyb gerne her hvad aktivitetstypen dækker over.",
    )
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)

    def __str__(self):
        return self.name

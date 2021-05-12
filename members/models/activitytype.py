# Added to support different types of activities.
# Makes is possible to filter certain activities out when showing the list to users.

from django.db import models


class ActivityType(models.Model):
    class Meta:
        verbose_name = "Aktivitetstype"
        verbose_name_plural = "Aktivitetstyper"
        ordering = ["display_name"]

    id = models.CharField(
        "id",
        primary_key=True,
        max_length=50,
        help_text="En sigende identifikator for aktivitetstypen. Fx 'STØTTEMEDLEM'.",
    )
    display_name = models.CharField(
        "Navn",
        max_length=100,
        help_text="Et visningsnavn for aktivitetstypen. Fx 'Støttemedlem'.",
    )
    description = models.CharField(
        "Beskrivelse",
        max_length=200,
        help_text="En beskrivelse af hvad aktivitetstypen dækker over.",
    )
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)

    def __str__(self):
        return self.display_name

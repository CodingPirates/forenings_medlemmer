from django.db import models
from django.utils import timezone


class Consent(models.Model):
    class Meta:
        verbose_name = "Privatlivspolitik"
        verbose_name_plural = "Privatlivspolitikker"
        ordering = ["-released_at"]

    released_at = models.DateTimeField(
        "Gældende fra",
        null=True,
        blank=True,
        help_text="Hvornår er denne privatlivspolitik gældende fra ?",
    )  # If no released_at value, the consent is a draft

    title = models.CharField("Titel", max_length=200)

    text = models.TextField(
        "Privatlivspolitik", help_text="Tekst for privatlivspolitik"
    )

    def is_active(self):
        return self.released_at is not None and self.released_at <= timezone.now()

    def __str__(self):
        return f"Consent ID: {self.id}"

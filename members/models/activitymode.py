from django.db import models


class ActivityMode(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Aktivitetsform"
        verbose_name_plural = "Aktivitetsformer"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.code})"

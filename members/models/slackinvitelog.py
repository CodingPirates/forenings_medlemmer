from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class SlackInviteLog(models.Model):
    STATUS_CHOICES = [
        (1, "Oprettet"),
        (2, "Invitation fejlede"),
        (3, "Fejl håndteret"),
        (4, "Slack invitation udført"),
    ]

    email = models.EmailField()
    purpose = models.CharField(max_length=255, blank=True)
    invite_url = models.URLField("Invite URL", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="slack_invite_logs",
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    message = models.TextField(blank=True)

    resolved = models.BooleanField(
        "Løst/håndteret",
        default=False,
        help_text="Marker hvis fejlen er håndteret/løst. Sættes automatisk hvis status er 'Invite used' eller 'Error handled'.",
    )
    resolved_at = models.DateTimeField(
        "Løst tidspunkt",
        null=True,
        blank=True,
        help_text="Tidspunkt hvor fejlen blev løst.",
    )
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="slack_invite_logs_resolved",
        verbose_name="Løst af",
        help_text="Bruger der har markeret fejlen som løst.",
    )
    resolution_note = models.TextField(
        "Løsningsnote", blank=True, help_text="Evt. kommentar eller note til løsningen."
    )

    class Meta:
        verbose_name = "Slack Invitation Log"
        verbose_name_plural = "Slack Invitation Logs"
        ordering = ["-created_at"]
        # Permission flyttes til SlackInvitationSetup for at matche ønsket placering

    def clean(self):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        emails = self.email.split()
        for e in emails:
            try:
                validate_email(e)
            except ValidationError:
                raise ValidationError({"email": f"Ugyldig emailadresse: {e}"})

    def email_summary(self):
        emails = self.email.split()
        if len(emails) == 1:
            return emails[0]
        return f"{len(emails)} emails"

    def __str__(self):
        emails = self.email.split()
        if len(emails) == 1:
            return f"{emails[0]} - {self.get_status_display()}"
        return f"{len(emails)} emails - {self.get_status_display()}"

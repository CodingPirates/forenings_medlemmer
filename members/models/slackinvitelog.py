from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class SlackInviteLog(models.Model):
    STATUS_CHOICES = [
        (1, "Created"),
        (2, "Invite used"),
        (3, "URL failed/email sent"),
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

    class Meta:
        verbose_name = "Slack Invite Log"
        verbose_name_plural = "Slack Invite Logs"
        ordering = ["-created_at"]
        permissions = [
            ("can_approve_slack_invites", "Can approve Slack invites"),
        ]

    def clean(self):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        emails = self.email.split()
        for e in emails:
            try:
                validate_email(e)
            except ValidationError:
                raise ValidationError({"email": f"Invalid email address: {e}"})

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

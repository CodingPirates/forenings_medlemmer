# from django.conf import settings
from django.db import models
from django.conf import settings


class SlackLog(models.Model):
    class Meta:
        permissions = (("can_approve_slack_invites", "Can approve Slack invitations"),)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    slack_user_id = models.CharField(
        max_length=64, help_text="Slack user ID for the invitee"
    )
    slack_email = models.EmailField(help_text="Email address of the invitee")
    action = models.CharField(max_length=32, help_text="Action taken, e.g. 'approved'")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(
        blank=True, help_text="Additional details or Slack API response"
    )

    def __str__(self):
        return f"{self.timestamp}: {self.user} {self.action} {self.slack_email}"

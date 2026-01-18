from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import hashlib

User = get_user_model()


class SlackInvitationSetup(models.Model):
    invite_url = models.URLField(
        "Slack Admin Invite URL",
        blank=True,
        help_text="URL for Slack admin invite page, e.g. https://yourteam.slack.com/sign_in_with_password?redir=%2Fadmin%2Finvites",
    )
    emails = models.TextField(
        "Notifikations Email Addresser",
        help_text="Space-separated list of allowed email addresses.",
        blank=True,
    )

    admin_username = models.EmailField(
        "Slack Admin Username",
        blank=True,
        help_text="Email address of the Slack admin user to log in as.",
    )
    admin_password_encrypted = models.BinaryField(
        "Slack Admin Password (Encrypted)",
        blank=True,
        null=True,
        help_text="Password for the Slack admin user (encrypted).",
    )
    updated_at = models.DateTimeField("Last Updated", auto_now=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="slack_invite_setups",
    )

    class Meta:
        verbose_name = "Slack Invitation Setup"
        verbose_name_plural = "Slack Invitation Setup"

    def __str__(self):
        return f"Slack Invitation Setup (Last updated: {self.updated_at})"

    def _get_fernet_key(self):
        # Use SHA256 of SECRET_KEY, then base64-encode digest for Fernet
        digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    @property
    def admin_password(self):
        if not self.admin_password_encrypted:
            return ""
        try:
            key = self._get_fernet_key()
            f = Fernet(key)
            encrypted = self.admin_password_encrypted
            if isinstance(encrypted, memoryview):
                encrypted = encrypted.tobytes()
            return f.decrypt(encrypted).decode("utf-8")
        except Exception as e:
            return f"[decryption error: {e}]"

    @admin_password.setter
    def admin_password(self, value):
        if value:
            key = self._get_fernet_key()
            f = Fernet(key)
            self.admin_password_encrypted = f.encrypt(value.encode("utf-8"))
        else:
            self.admin_password_encrypted = b""

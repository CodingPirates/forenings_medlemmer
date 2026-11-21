from django.conf import settings
from django.db import models


class AuthLog(models.Model):
    class Meta:
        verbose_name = "Login-log"
        verbose_name_plural = "Login-log"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["identifier", "created_at"])]

    class Event(models.TextChoices):
        LOGIN_OK = "login_ok", "Login OK"
        LOGIN_FAILED = "login_failed", "Login fejlet"
        CODE_FAILED = "code_failed", "Forkert kode"
        CODE_LOCKOUT = "code_lockout", "Låst efter for mange forkerte koder"
        CODE_REJECTED_LOCKED = "code_rejected_locked", "Kode afvist (låst)"
        CODE_REQUEST_BLOCKED = "code_request_blocked", "Kodeanmodning afvist (låst)"
        CODE_EXPIRED = "code_expired", "Kode udløbet"
        CODE_OK_NO_AUTOLOGIN = (
            "code_ok_no_autologin",
            "Kode OK, ingen auto-login (staff/superbruger)",
        )

    created_at = models.DateTimeField("Tidspunkt", auto_now_add=True)
    event = models.CharField("Hændelse", max_length=30, choices=Event.choices)
    success = models.BooleanField("Lykkedes", default=False)
    method = models.CharField("Metode", max_length=20, blank=True)
    identifier = models.CharField("Brugernavn/email", max_length=254, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Bruger",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    ip_address = models.GenericIPAddressField("IP-adresse", null=True, blank=True)
    user_agent = models.CharField("Browser", max_length=255, blank=True)

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} {self.event} {self.identifier}"

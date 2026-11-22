# myapp/models/permissions.py
from django.contrib.auth.models import User


class UserWithSuperuserView(User):
    class Meta:
        proxy = True
        verbose_name = "Bruger"
        verbose_name_plural = "Brugere"
        permissions = [
            ("view_superuser_status", "Kan se og filtrere på is_superuser"),
        ]

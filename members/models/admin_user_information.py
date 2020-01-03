from django.db import models
from django.conf import settings

from .union import Union
from .department import Department


class AdminUserInformation(models.Model):
    def __str__(self):
        return self.user.username + " admin data"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    departments = models.ManyToManyField(Department, blank=True)
    unions = models.ManyToManyField(Union, blank=True)

from django.db import models
from django.conf import settings

from . import Union, Department


class AdminUserInformation(models.Model):
    def __str__(self):
        return self.user.username + " admin data"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    departments = models.ManyToManyField(Department)
    unions = models.ManyToManyField(Union)

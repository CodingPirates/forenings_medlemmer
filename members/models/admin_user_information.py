from django.db import models
from django.conf import settings

from .union import Union
from .department import Department


class AdminUserInformation(models.Model):
    def __str__(self):
        return self.user.username + " admin data"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, blank=True)
    unions = models.ManyToManyField(Union, blank=True)

    @staticmethod
    def get_departments_admin(user):
        if user.is_superuser:
            return Department.objects.all()
        else:
            return Department.objects.filter(adminuserinformation__user=user)

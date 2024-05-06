from django.db import models
from django.conf import settings

from .union import Union
from .department import Department


class AdminUserInformation(models.Model):
    def __str__(self):
        return self.user.username + " admin data"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    departments = models.ManyToManyField(
        Department, blank=True, verbose_name="Afdelinger"
    )
    unions = models.ManyToManyField(Union, blank=True, verbose_name="Foreninger")

    @staticmethod
    def get_departments_admin(user):
        if user.is_superuser or user.has_perm("members.view_all_departments"):
            return Department.objects.all()
        else:
            return Department.objects.filter(adminuserinformation__user=user)

    @staticmethod
    def get_unions_admin(user):
        if user.is_superuser or user.has_perm("members.view_all_unions"):
            return Union.objects.all()
        else:
            return Union.objects.filter(adminuserinformation__user=user)

from django.contrib.auth.base_user import BaseUserManager
from members.models.family import Family


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('A email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        # This is a workaround for Django not automaticly looking up family instance by primary key
        if type(extra_fields.get('family')) is not Family:
            extra_fields['family'] = Family.objects.get(pk=extra_fields.get('family'))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser can not be False. Use create_user if you wan\'t to control is_superuser')

        return self._create_user(email, password, **extra_fields)

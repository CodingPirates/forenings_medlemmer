from django.core.management.base import BaseCommand
from members.models.person import Person
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Creates a User for every Person that is of type PARENT or GUARDIAN and has a unique email"

    def handle(self, *args, **options):
        for person in Person.objects.filter(
            membertype__in=[Person.PARENT, Person.GUARDIAN]
        ):
            if person.user:
                continue  # Person already has a user

            if (
                person.email
                and Person.objects.filter(
                    email=person.email, membertype__in=[Person.PARENT, Person.GUARDIAN]
                ).count()
                > 1
            ):
                continue  # Ignore people with duplicate email

            user = User.objects.create_user(username=person.email, email=person.email)
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            person.user = user
            person.save()

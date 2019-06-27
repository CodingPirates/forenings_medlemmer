from django.core.management.base import BaseCommand
from members.models.person import Person


class Command(BaseCommand):
    help = "Finds parent and guardians with duplicate emails"

    def handle(self, *args, **options):
        print("pk,email")

        for person in Person.objects.filter(
            membertype__in=[Person.PARENT, Person.GUARDIAN]
        ):
            if person.email and Person.objects.filter(email=person.email).count() < 2:
                continue  # Ignore people with unique emails

            print(str(person.pk) + "," + person.email)

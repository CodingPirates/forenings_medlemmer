from django.core.management.base import BaseCommand
from members.models.person import Person
from members.models.family import Family


class Command(BaseCommand):
    help = "Finds families who has no email at all and print the familys pk"

    def handle(self, *args, **options):
        for family in Family.objects.all():
            if family.email:
                continue

            has_email = False
            for person in Person.objects.filter(family=family):
                if person.email:
                    has_email = True
                    break

            if not has_email:
                print(family.pk)

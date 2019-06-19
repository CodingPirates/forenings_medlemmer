from django.core.management.base import BaseCommand
from members.models.person import Person
from members.models.family import Family


class Command(BaseCommand):
    help = "Finds families who has no person who can login, and print the familys pk"

    def handle(self, *args, **options):
        for family in Family.objects.all():
            if Person.objects.filter(family=family, user__isnull=False).count() == 0:
                print(family.pk)

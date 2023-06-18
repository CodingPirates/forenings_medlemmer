from django.core.management.base import BaseCommand
from members.models.person import Person


class Command(BaseCommand):
    help = "Update a User with null Gender to Gender OT"

    def handle(self, *args, **options):
        for person in Person.objects.filter(gender=None):
            person.gender = Person.OTHER_GENDER
            person.save()

        for person in Person.objects.filter(gender=""):
            person.gender = Person.OTHER_GENDER
            person.save()

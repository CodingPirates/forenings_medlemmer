from django.core.management.base import BaseCommand
from members.models import Person

# run locally:
# docker compose run web ./manage.py set_person_municipality


class Command(BaseCommand):
    help = "Set the municipality for all persons based on their address"

    def handle(self, *args, **options):
        # Iterate over all items in Person model
        for person in Person.objects.all():
            self.stdout.write("Updating record for " + str(person))
            person.update_dawa_data(force=True)

        self.stdout.write(
            self.style.SUCCESS("Successfully updated municipality for all persons")
        )

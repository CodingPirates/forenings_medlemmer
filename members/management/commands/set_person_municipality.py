from django.core.management.base import BaseCommand
import requests
from members.models import Municipality, Person

# run locally:
# docker compose run web ./manage.py set_person_municipality


class Command(BaseCommand):
    help = "Set the municipality for all persons based on their address"

    def handle(self, *args, **options):
        # Iterate over all items in Person model
        for person in Person.objects.all():
            # First reset municipality before migrating data
            person.municipality = None
            person.save()

            # Call the API to get municipality id
            url = f"https://api.dataforsyningen.dk/adresser?id={person.dawa_id}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                if not data:
                    self.stdout.write(
                        self.style.ERROR(
                            f"No DAWA data found for person: {person.name} - {url}"
                        )
                    )
                    continue

                municipality_id = data[0]["adgangsadresse"]["kommune"]["kode"]

                if municipality_id:
                    try:
                        # Look up the found municipality id from Municipality model
                        municipality = Municipality.objects.get(dawa_id=municipality_id)
                        # Set the municipality for the person
                        person.municipality = municipality
                        person.save()
                        self.stdout.write(
                            f"Set municipality for person: {person.name} to {municipality.name}"
                        )
                    except Municipality.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Municipality with dawa_id {municipality_id} does not exist."
                            )
                        )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to fetch data for person: {person.name} - {url}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("Successfully updated municipality for all persons")
        )

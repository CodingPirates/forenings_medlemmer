from django.core.management.base import BaseCommand
import requests
from members.models import Person

# run locally:
# docker compose run web ./manage.py set_person_region


class Command(BaseCommand):
    help = "Set the region for all persons based on their address"

    def handle(self, *args, **options):
        # Iterate over all items in Person model
        for person in Person.objects.filter(dawa_id__isnull=False).exclude(dawa_id=""):
            # for person in Person.objects.all():
            # First reset region before migrating data
            person.region = None
            person.save()

            # Call the API to get region name
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

                region = data[0]["adgangsadresse"]["region"]["navn"]

                if region:
                    # try:
                    # Look up the found region name from Municipality model
                    # municipality = Municipality.objects.get(dawa_id=region_id)
                    # Set the region for the person
                    person.region = region
                    person.save()
                    self.stdout.write(
                        f"Set region for person: {person.name} to {region}"
                    )
                # except Municipality.DoesNotExist:
                #    self.stdout.write(
                #        self.style.ERROR(
                #            f"Municipality with dawa_id {region_id} does not exist."
                #        )
                #    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to fetch data for person: {person.name} - {url}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("Successfully updated region for all persons")
        )

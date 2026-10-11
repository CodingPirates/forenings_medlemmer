from django.core.management.base import BaseCommand
from members.models.address import Address


# run locally:
# docker compose run web ./manage.py update_ext_address_info


class Command(BaseCommand):
    help = "Update external address data on all addresses in the address model"

    def handle(self, *args, **options):
        for address in Address.objects.all():
            self.stdout.write("Updating record for " + str(address))
            address.get_ext_address_data()

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully updated address information for all addresses"
            )
        )

from django.core.management.base import BaseCommand

from members.models import (
    Person,
)


class Command(BaseCommand):
    help = "Updates DAWA data to ensure correct address information"

    def handle(self, *args, **options):
        persons = (  # noqa: F841,E261
            Person.objects.filter(municipality__isnull=True)
            .exclude(streetname__exact="")
            .exclude(address_invalid__exact=True)[:50]
        )  # noqa: F841

        for person in persons:
            person.update_dawa_data()

from django.core.management.base import BaseCommand
from members.models import Address
from tqdm import tqdm


class Command(BaseCommand):
    help = "Gathers daily statistics"

    def handle(self, *args, **options):
        for addres in tqdm(Address.objects.all(), desc="Updating address"):
            addres.save()

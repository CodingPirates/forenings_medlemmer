from django.core.management.base import BaseCommand
from members.models.statistics import gatherDayliStatistics


class Command(BaseCommand):
    help = "Gathers daily statistics"

    def handle(self, *args, **options):
        gatherDayliStatistics()
        print("Stats generated")

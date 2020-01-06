from django.core.management.base import BaseCommand
from members.models.statistics import gatherDayliStatistics

""" A scheduler on heroku is set to run this command once per day """


class Command(BaseCommand):
    help = "Gathers daily statistics"

    def handle(self, *args, **options):
        gatherDayliStatistics()
        print("Stats generated")

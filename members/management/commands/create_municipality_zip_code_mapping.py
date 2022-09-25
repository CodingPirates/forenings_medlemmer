from django.core.management.base import BaseCommand
import datetime


class Command(BaseCommand):
    help = "Creates a mapping table to determine the main zip code for a municipality."


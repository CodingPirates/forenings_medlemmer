from django.core.management.base import BaseCommand

from members.models import (
    EmailItem,
)

class Command(BaseCommand):
    help = "Send pending emails"

    def handle(self, *args, **options):
        for curEmail in EmailItem.objects.filter(sent_dtm=None):
            curEmail.send()

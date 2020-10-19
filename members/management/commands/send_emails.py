from django.core.management.base import BaseCommand

from members.models import PayableItem


class Command(BaseCommand):
    help = "Send emails in queue"

    def handle(self, *args, **options):
        PayableItem.send_all_payment_confirmations()

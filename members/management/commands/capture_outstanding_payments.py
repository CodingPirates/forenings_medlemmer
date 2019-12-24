from django.core.management.base import BaseCommand
from members.models.payment import Payment


class Command(BaseCommand):
    help = "Capture all outstanding payments - on those payments without autocapture."

    def handle(self, *args, **options):
        Payment.capture_oustanding_payments()

import datetime

from django.core.management.base import BaseCommand

from members.models import (
    Payment,
)


class Command(BaseCommand):
    help = "If a person sign up and pay before the end of the year, a payment is created but not captured. Capture all outstanding payments at the beginning of the year."

    def handle(self, *args, **options):
        today = datetime.date.today()
        if (today.month, today.day) == (1, 1):
            Payment.capture_oustanding_payments()

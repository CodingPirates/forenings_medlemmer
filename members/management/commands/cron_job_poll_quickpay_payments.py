import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from members.models import (
    Payment,
)


class Command(BaseCommand):
    help = "Poll Quickpay payments which did not recieve callback"

    def handle(self, *args, **options):
        outdated_dtm = timezone.now() - datetime.timedelta(
            days=14
        )  # Timeout checking payments after 14 days
        payments = Payment.objects.filter(
            rejected_at__isnull=True,
            confirmed_at__isnull=True,
            payment_type=Payment.CREDITCARD,
            added_at__gt=outdated_dtm,
        )

        for payment in payments:
            payment.get_quickpaytransaction().update_status()

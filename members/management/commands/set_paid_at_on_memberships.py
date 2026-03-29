from django.core.management.base import BaseCommand

from members.models.payment import Payment

# run command locally in Docker:
# docker compose run web ./manage.py anonymize_families_without_consent --dry-run


class Command(BaseCommand):
    help = "Set paid_at on memberships where payment has been received"

    def handle(self, *args, **options):
        payments = Payment.objects.exclude(confirmed_at__isnull=True).exclude(
            member__isnull=True
        )
        for payment in payments:
            payment.member.paid_at = payment.confirmed_at
            payment.member.save()

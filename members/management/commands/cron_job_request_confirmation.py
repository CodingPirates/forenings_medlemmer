import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q, F

from members.models import (
    EmailTemplate,
    Family,
    Notification,
)


class Command(BaseCommand):
    help = "Ask families to confirm their details"

    def handle(self, *args, **options):
        # Find all Families, which has an updated_dtm older than the specified time for updates from today.
        # Exclude the families which has already received a notification after they updated last.
        # (to avoid sending again)
        outdated_dtm = timezone.now() - datetime.timedelta(
            days=settings.REQUEST_FAMILY_VALIDATION_PERIOD
        )
        unconfirmed_families = Family.objects.filter(
            Q(confirmed_at__lt=outdated_dtm) | Q(confirmed_at=None)
        ).exclude(
            Q(notification__update_info_dtm__gt=F("confirmed_at"))
            | Q(~Q(notification__update_info_dtm=None), confirmed_at=None)
        )[
            :10
        ]

        # send notification to all families asking them to update
        # their family details
        for family in unconfirmed_families:
            emails = EmailTemplate.objects.get(idname="UPDATE_DATA").makeEmail(
                family, {}
            )
            for email in emails:
                notification = Notification(
                    family=family, email=email, update_info_dtm=timezone.now()
                )
                notification.save()

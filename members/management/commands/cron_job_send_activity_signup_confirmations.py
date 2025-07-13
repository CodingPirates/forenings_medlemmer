from django.core.management.base import BaseCommand

from members.models import (
    ActivityParticipant,
    EmailTemplate,
    Notification,
)


class Command(BaseCommand):
    help = "Sends activity signup confirmations to participants"

    def handle(self, *args, **options):
        unannounced_signups = ActivityParticipant.objects.exclude(
            notification__isnull=False
        ).filter(payment__accepted_at__isnull=False)

        for announcement in unannounced_signups:
            context = {
                "activity": announcement.activity,
                "person": announcement.person,
                "family": announcement.person.family,
                "union": announcement.activity.department.union,
            }
            emails = EmailTemplate.objects.get(idname="ACT_CONFIRM").makeEmail(
                [announcement.person, announcement.person.family], context
            )
            for email in emails:
                notification = Notification(
                    family=announcement.person.family,
                    email=email,
                    anounced_activity_participant=announcement,
                )
                notification.save()

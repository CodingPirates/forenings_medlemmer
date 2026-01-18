from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from members.models import (
    ActivityInvite,
    EmailTemplate,
)


class Command(BaseCommand):
    help = "Send activity invite reminders"

    def handle(self, *args, **options):
        print("Sending activity invite reminders")
        template_name = "ACT_INVITE"
        try:
            template = EmailTemplate.objects.get(idname=template_name)
        except EmailTemplate.DoesNotExist:
            print(f"Email template '{template_name}' does not exist")
            return

        # override template subject
        template.subject = f"Påmindelse: {template.subject}"

        # Find invites which will expire in the next 3 days
        now = timezone.now().date()
        three_days_from_now = now + timedelta(days=3)
        invites = ActivityInvite.objects.filter(
            reminder_sent_at__isnull=True,
            expire_dtm__lte=three_days_from_now,
        ).exclude(expire_dtm__lt=now)

        for invite in invites:
            context = {
                "activity": invite.activity,
                "activity_invite": invite,
                "invite": invite,
                "person": invite.person,
                "family": invite.person.family,
                "union": invite.activity.department.union,
            }
            print(
                f"Sending reminder for activity '{invite.activity.department.name}/{invite.activity.name}' to person '{invite.person.name}'"
            )
            template.makeEmail(
                [invite.person.family], context, allow_multiple_emails=True
            )
            invite.reminder_sent_at = timezone.now().date()
            invite.save()

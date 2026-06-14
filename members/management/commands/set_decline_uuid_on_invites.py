import uuid

from django.core.management.base import BaseCommand

from members.models.activityinvite import ActivityInvite


class Command(BaseCommand):
    help = "Set a new decline_uuid on all activity invites that do not have one"

    def handle(self, *args, **options):
        invites = ActivityInvite.objects.filter(decline_uuid=None)
        count = invites.count()

        for invite in invites:
            invite.decline_uuid = uuid.uuid4()
            invite.save()

        self.stdout.write(self.style.SUCCESS(f"Updated {count} invites"))

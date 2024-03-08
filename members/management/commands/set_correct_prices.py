from django.core.management.base import BaseCommand
from members.models.activityinvite import ActivityInvite


class Command(BaseCommand):
    help = "This command populates the price in dkk for the activity invites based on the activities if no note has been made. This is due to wrong code"

    def handle(self, *args, **options):
        for activityInvite in ActivityInvite.objects.all():
            if activityInvite.price_note == "":
                activityInvite.price_in_dkk = activityInvite.activity.price_in_dkk
                activityInvite.save()

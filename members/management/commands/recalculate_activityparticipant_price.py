from django.core.management.base import BaseCommand
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant


class Command(BaseCommand):
    help = "Recalculate the price for all activity participants, so we display the correct price even if they got an invitation with another price."

    def handle(self, *args, **options):
        for activity_participant in ActivityParticipant.objects.all():
            # Find matching activity invite
            activity_invite = ActivityInvite.objects.filter(
                activity=activity_participant.activity,
                person=activity_participant.person,
            ).first()
            if activity_invite:
                activity_participant.price_in_dkk = activity_invite.price_in_dkk
            activity_participant.save()

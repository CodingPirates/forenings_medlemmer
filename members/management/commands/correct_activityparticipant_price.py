from datetime import date
from django.core.management.base import BaseCommand
from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant


class Command(BaseCommand):
    help = "Unfortunately, prices in the activity participants table are incorrect. This is a one time command, that fixes that."

    def handle(self, *args, **kwargs):
        # Correct activity participant prices
        activities = Activity.objects.all()

        for activity in activities:
            activityparticipants = ActivityParticipant.objects.filter(activity=activity)

            for activityparticipant in activityparticipants:
                self.correct_activityparticipant_prices(activityparticipant)

    def correct_activityparticipant_prices(self, activityparticipant):
        invite = ActivityInvite.objects.filter(
            activity=activityparticipant.activity, person=activityparticipant.person
        ).first()

        if not invite:
            activityparticipant.price_in_dkk = activityparticipant.activity.price_in_dkk
        else:
            activityparticipant.price_in_dkk = (
                activityparticipant.activity.price_in_dkk
                if invite.price_in_dkk == activityparticipant.price_in_dkk
                else invite.price_in_dkk
            )
        activityparticipant.save()

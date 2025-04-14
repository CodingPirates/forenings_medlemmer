from datetime import date
from django.conf import settings
from django.core.management.base import BaseCommand
from members.models.activity import Activity
from members.models.activityparticipant import ActivityParticipant
from members.models.member import Member
from members.models.payment import Payment


class Command(BaseCommand):
    help = "Creates all existing memberships when migrating to new membership structure"

    def handle(self, *args, **kwargs):
        # Move members from activities
        membership_activities = Activity.objects.filter(
            activitytype="FORENINGSMEDLEMSKAB"
        ) | Activity.objects.filter(activitytype="FORLØB")

        for activity in membership_activities:
            activityparticipants = ActivityParticipant.objects.filter(activity=activity)

            for activityparticipant in activityparticipants:
                self.create_membership_if_not_exists(activityparticipant)

    def create_membership_if_not_exists(self, activityparticipant):
        if not Member.objects.filter(
            union=activityparticipant.activity.union,
            person=activityparticipant.person,
            member_since__year=activityparticipant.added_at.year,
        ).exists():
            payment = Payment.objects.filter(
                activity=activityparticipant.activity,
                activityparticipant=activityparticipant,
            )

            if payment.exists():
                amount = payment.first().amount_ore / 100
                paid_at = payment.first().confirmed_at
            else:
                amount = activityparticipant.activity.price_in_dkk
                paid_at = None

            Member.objects.create(
                union=activityparticipant.activity.union,
                person=activityparticipant.person,
                member_since=activityparticipant.added_at,
                member_until=date(activityparticipant.added_at.year, 12, 31),
                price_in_dkk=amount,
                paid_at=paid_at,
            )

            if activityparticipant.activity.activitytype == "FORLØB":
                activityparticipant.price_in_dkk = (
                    activityparticipant.activity.price_in_dkk
                    - settings.MINIMUM_MEMBERSHIP_PRICE_IN_DKK
                )
                activityparticipant.save()

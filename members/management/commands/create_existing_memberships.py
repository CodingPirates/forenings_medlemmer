from datetime import date
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
            activitytype__in=["FORENINGSMEDLEMSKAB", "FORLØB"]
        )

        for activity in membership_activities:
            activityparticipants = ActivityParticipant.objects.filter(activity=activity)

            for activityparticipant in activityparticipants:
                self.create_membership_if_not_exists(activityparticipant)

    def create_membership_if_not_exists(self, activityparticipant):
        if activityparticipant.activity.activitytype_id == "FORLØB":
            union = activityparticipant.activity.department.union
            amount = 0
        else:
            union = activityparticipant.activity.union
            amount = activityparticipant.activity.union.membership_price_in_dkk

        if not Member.objects.filter(
            union=union,
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
                paid_at = None

            Member.objects.create(
                union=union,
                person=activityparticipant.person,
                member_since=(
                    activityparticipant.added_at
                    if activityparticipant.activity.start_date.year
                    == activityparticipant.added_at.year
                    else date(activityparticipant.activity.start_date.year, 1, 1)
                ),
                member_until=date(activityparticipant.activity.start_date.year, 12, 31),
                price_in_dkk=amount,
                paid_at=paid_at,
            )

from django.core.management.base import BaseCommand
from members.models.union import Union
from members.models.activity import Activity
from members.models.activitytype import ActivityType
from members.models.department import Department
import datetime


class Command(BaseCommand):
    help = "Closes memberships for this year"
    output_transaction = True

    def handle(self, *args, **options):
        for curMembershipActivity in Activity.objects.filter(
            activitytype="FORENINGSMEDLEMSKAB"
        ).filter(start_date=datetime.date(year=2024, month=1, day=1)):
            curMembershipActivity.visible = False
            curMembershipActivity.save()

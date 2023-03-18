from django.core.management.base import BaseCommand
from members.models.activityparticipant import ActivityParticipant


class Command(BaseCommand):
    help = "Populates the person field on the activity participants table, so we can remove member in the future"

    def handle(self, *args, **options):
        for actpar in ActivityParticipant.objects.all():
            actpar.person = actpar.member.person
            actpar.save()

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from members.models import (
    ActivityParticipant,
)

class Command(BaseCommand):
    help = 'Delete note field after end of activity due to GDPR.'

    def handle(self, *args, **options):
        participants = (
            ActivityParticipant.objects.filter(note__isnull=False)
            .exclude(note__exact="")
            .filter(activity__end_date__lt=timezone.now() - timedelta(days=14))
        )

        for participant in participants:
            participant.note = ""
            participant.save()

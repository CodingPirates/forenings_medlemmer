from django.utils import timezone

from members.models.activityparticipant import ActivityParticipant


def get_missing_payments_for_family(family_id):
    missing_payments = ActivityParticipant.objects.filter(
        person__family_id=family_id,
        activity__end_date__gt=timezone.now(),
        payment__accepted_at=None,
    )
    return missing_payments

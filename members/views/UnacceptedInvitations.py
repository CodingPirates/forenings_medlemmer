from django.utils import timezone
from django.db.models import OuterRef, Exists

from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant


def get_unaccepted_invitations_for_family(family_id):
    participant_subquery = ActivityParticipant.objects.filter(
        person__family_id=family_id,
        person_id=OuterRef("person_id"),
        activity_id=OuterRef("activity_id"),
    )

    # Get invitations where the participant record does not exist
    unaccepted_invitations = (
        ActivityInvite.objects.filter(
            person__family_id=family_id,
            expire_dtm__gte=timezone.now(),
            rejected_at=None,
        )
        .annotate(is_participant=Exists(participant_subquery))
        .filter(is_participant=False)
    )

    return unaccepted_invitations

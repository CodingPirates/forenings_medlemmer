import json

from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType


def log_volunteer_contact_preference_change(request, volunteer):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return

    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(volunteer).pk,
        object_id=volunteer.pk,
        object_repr=str(volunteer),
        action_flag=CHANGE,
        change_message=json.dumps(
            [{"changed": {"fields": ["Må Coding Pirates Denmark kontakte mig?"]}}]
        ),
    )

import json

from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType


def log_person_contact_preference_change(request, person, changed_fields):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return

    if not changed_fields:
        return

    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(person).pk,
        object_id=person.pk,
        object_repr=str(person),
        action_flag=CHANGE,
        change_message=json.dumps([{"changed": {"fields": changed_fields}}]),
    )

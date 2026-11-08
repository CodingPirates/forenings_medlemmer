import json

from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from members.models.volunteerrequestitem import VolunteerRequestItem
from members.utils.user import user_to_person


@login_required
def volunteerRequestCancel(request, item_id):
    try:
        family = user_to_person(request.user).family
        item = VolunteerRequestItem.objects.select_related(
            "volunteer_request__person", "department", "activity"
        ).get(
            pk=item_id,
            status="NEW",
            volunteer_request__person__family=family,
            volunteer_request__person__deleted_dtm__isnull=True,
        )
    except (VolunteerRequestItem.DoesNotExist, AttributeError):
        return HttpResponseForbidden(
            "Du kan kun annullere afventende anmodninger for din egen familie."
        )

    if request.method == "POST":
        old_status = item.get_status_display()
        item.status = "NOT_INTERESTED"
        item.finished = timezone.now()
        item.save(update_fields=["status", "finished"])

        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(item).pk,
            object_id=item.pk,
            object_repr=str(item),
            action_flag=CHANGE,
            change_message=json.dumps(
                [
                    {
                        "changed": {
                            "fields": [
                                f"Status: {old_status} → {item.get_status_display()} (annulleret af bruger)"
                            ]
                        }
                    }
                ]
            ),
        )
        return HttpResponseRedirect(reverse("volunteer_signup"))

    return render(
        request,
        "members/volunteer_request_cancel.html",
        {"item": item, "person": item.volunteer_request.person},
    )

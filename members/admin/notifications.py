from django.urls import reverse

from members.models import AdminUserInformation, VolunteerRequestItem


def get_admin_notifications(request):
    notifications = []

    if (
        request is None
        or not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return notifications

    user = request.user
    pending_requests = VolunteerRequestItem.objects.filter(status="NEW")

    if not (user.is_superuser or user.has_perm("members.view_all_departments")):
        pending_requests = pending_requests.filter(
            department__in=AdminUserInformation.get_departments_admin(user)
        )

    pending_count = pending_requests.count()
    if pending_count:
        notifications.append(
            {
                "level": "warning",
                "label": f"{pending_count} nye frivillig-anmodninger",
                "url": f"{reverse('admin:members_volunteerrequestitem_changelist')}?status__exact=NEW",
            }
        )

    return notifications

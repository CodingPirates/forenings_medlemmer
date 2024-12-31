from django.http import JsonResponse
from members.models import Activity


def activity_by_department(request, department_id):
    activities = Activity.objects.filter(
        department_id=department_id, activitytype__id__in=["FORLØB", "ARRANGEMENT"]
    ).order_by("-start_date", "name")
    data = {
        "activities": [
            {
                "id": activity.id,
                "name": activity.name # f"[{activity.start_date} - {activity.end_date}] {activity.name}",
            }
            for activity in activities
        ]
    }
    return JsonResponse(data)

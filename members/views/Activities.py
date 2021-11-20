import datetime
from django.shortcuts import render
from django.utils import timezone

from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models import Person
from members.utils.user import user_to_person


def Activities(request):
    current_activities = Activity.objects.filter(
        signup_closing__gte=timezone.now(),
        activitytype__in=["FORLØB", "ARRANGEMENT"],
    ).order_by("start_date")

    family = None
    invites = None
    participating = None
    current_activities_with_persons = current_activities
    if request.user.is_authenticated:
        family = user_to_person(request.user).family
        invites = ActivityInvite.objects.filter(
            person__family=family, expire_dtm__gte=timezone.now(), rejected_dtm=None
        )
        participating = ActivityParticipant.objects.filter(
            member__person__family=family,
            activity__activitytype__in=["FORLØB", "ARRANGEMENT"],
        ).order_by("-activity__start_date")

        current_activities_with_persons = []
        # augment open invites with the persons who could join it in the family
        for curActivity in current_activities:
            applicablePersons = Person.objects.filter(
                family=family,  # only members of this family
                birthday__lte=timezone.now()
                - datetime.timedelta(days=curActivity.min_age * 365),  # old enough
                birthday__gt=timezone.now()
                - datetime.timedelta(days=curActivity.max_age * 365),  # not too old
            ).exclude(
                member__activityparticipant__activity=curActivity
            )  # not already participating

            if applicablePersons.exists():
                current_activities_with_persons.append(
                    {
                        "id": curActivity.id,
                        "name": curActivity.name,
                        "open_invite": curActivity.open_invite,
                        "department": curActivity.department,
                        "persons": applicablePersons,
                    }
                )

    context = {
        "family": family,
        "invites": invites,
        "participating": participating,
        "current_activities": current_activities_with_persons,
    }
    return render(request, "members/activities.html", context)

import datetime
from django.shortcuts import render
from django.utils import timezone

from members.models.activity import Activity
from members.models.activityparticipant import ActivityParticipant
from members.models import Person
from members.utils.user import user_to_person


def SupportMembership(request):
    current_activities = Activity.objects.filter(
        signup_closing__gte=timezone.now(),
        activitytype__in=["STØTTEMEDLEMSKAB"],
    ).order_by("zipcode")

    family = None
    participating = None
    activities_with_persons = current_activities
    if request.user.is_authenticated:
        family = user_to_person(request.user).family

        participating = ActivityParticipant.objects.filter(
            member__person__family=family,
            activity__activitytype__in=["STØTTEMEDLEMSKAB"],
        ).order_by("-activity__start_date")

        activities_with_persons = []
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
                activities_with_persons.append(
                    {
                        "id": curActivity.id,
                        "name": curActivity.name,
                        "union": curActivity.union,
                        "persons": applicablePersons,
                    }
                )

    context = {
        "family": family,
        "participating": participating,
        "current_activities": activities_with_persons,
    }
    return render(request, "members/support_membership.html", context)

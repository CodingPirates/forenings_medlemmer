import datetime
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models import Person
from members.utils.user import user_to_person, has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def Activities(request):
    family = user_to_person(request.user).family
    invites = ActivityInvite.objects.filter(
        person__family=family, expire_dtm__gte=timezone.now(), rejected_dtm=None
    )
    open_activities = Activity.objects.filter(
        open_invite=True, signup_closing__gte=timezone.now()
    ).order_by("zipcode")
    participating = ActivityParticipant.objects.filter(
        member__person__family=family
    ).order_by("-activity__start_date")

    open_activities_with_persons = []
    # augment open invites with the persons who could join it in the family
    for curActivity in open_activities:
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
            open_activities_with_persons.append(
                {
                    "id": curActivity.id,
                    "name": curActivity.name,
                    "department": curActivity.department,
                    "persons": applicablePersons,
                }
            )

    context = {
        "family": family,
        "invites": invites,
        "participating": participating,
        "open_activities": open_activities_with_persons,
    }
    return render(request, "members/activities.html", context)

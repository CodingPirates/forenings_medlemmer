from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

from members.models.activity import Activity
from members.models.activityparticipant import ActivityParticipant
from members.models import Person
from members.utils.user import user_to_person, has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def SupportMembership(request):
    family = user_to_person(request.user).family
    activities = Activity.objects.filter(
        signup_closing__gte=timezone.now(),
        activitytype__in=["STØTTEMEDLEMSKAB"],
    ).order_by("zipcode")
    participating = ActivityParticipant.objects.filter(
        member__person__family=family,
        activity__activitytype__in=["STØTTEMEDLEMSKAB"],
    ).order_by("-activity__start_date")

    activities_with_persons = []
    # augment open invites with the persons who could join it in the family
    for curActivity in activities:
        applicablePersons = Person.objects.filter(
            family=family,  # only members of this family
            birthday__lte=curActivity.start_date
            - relativedelta(years=curActivity.min_age),  # old enough
            birthday__gt=curActivity.start_date
            - relativedelta(years=curActivity.max_age + 1),  # not too old
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
        "participating": participating,
        "activities": activities_with_persons,
    }
    return render(request, "members/support_membership.html", context)

from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone

from members.models.activity import Activity
from members.models.activityparticipant import ActivityParticipant
from members.models import Person
from members.utils.user import user_to_family

from django.contrib.auth.decorators import user_passes_test
from members.utils.user import is_not_logged_in_and_has_person


@user_passes_test(is_not_logged_in_and_has_person, "/admin_signup/")
def SupportMembership(request):
    current_activities = Activity.objects.filter(
        signup_closing__gte=timezone.now(),
        activitytype__in=["STØTTEMEDLEMSKAB"],
    ).order_by("start_date")

    family = None
    participating = None
    activities_with_persons = current_activities
    if request.user.is_authenticated:
        family = user_to_family(request.user)

        participating = ActivityParticipant.objects.filter(
            person__family=family,
            activity__activitytype__in=["STØTTEMEDLEMSKAB"],
            person__anonymized=False,
        ).order_by("-activity__start_date")

        activities_with_persons = []
        # augment open invites with the persons who could join it in the family
        for curActivity in current_activities:
            applicablePersons = Person.objects.filter(
                family=family,  # only members of this family
                birthday__lte=curActivity.start_date
                - relativedelta(years=curActivity.min_age),  # old enough
                birthday__gt=curActivity.start_date
                - relativedelta(years=curActivity.max_age + 1),  # not too old
            ).exclude(
                activityparticipant__activity=curActivity
            )  # not already participating

            if applicablePersons.exists():
                activities_with_persons.append(
                    {
                        "id": curActivity.id,
                        "name": curActivity.name,
                        "union": curActivity.union,
                        "persons": applicablePersons,
                        "price_in_dkk": curActivity.price_in_dkk,
                    }
                )

    context = {
        "family": family,
        "participating": participating,
        "current_activities": activities_with_persons,
    }
    return render(request, "members/support_membership.html", context)

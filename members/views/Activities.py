from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone

from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models import (
    Person,
    WaitingList,
)
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
    children = []

    if request.user.is_authenticated:
        person = user_to_person(request.user)

        if person:
            family = person.family
            children = [
                {"person": child, "waitinglists": WaitingList.get_by_child(child)}
                for child in family.get_children()
            ]
            for child in children:
                child["departments_is_waiting"] = [
                    department for (department, _place) in child["waitinglists"]
                ]
                child["participating_activities"] = [
                    (act.activity.id)
                    for act in ActivityParticipant.objects.filter(member__person=child["person"].id)
                ]
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
                    birthday__lte=curActivity.start_date
                    - relativedelta(years=curActivity.min_age),  # old enough
                    birthday__gt=curActivity.start_date
                    - relativedelta(years=curActivity.max_age + 1),  # not too old
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
                            "min_age": curActivity.min_age,
                            "max_age": curActivity.max_age,
                        }
                    )

    context = {
        "family": family,
        "invites": invites,
        "participating": participating,
        "current_activities": current_activities_with_persons,
        "children": children,
    }
    return render(request, "members/activities.html", context)

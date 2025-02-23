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

import requests
import json


def Activities(request):
    current_activities = Activity.objects.filter(
        signup_closing__gte=timezone.now(),
        end_date__gte=timezone.now(),
        activitytype__in=["FORLØB", "ARRANGEMENT"],
        visible=True,
        visible_from__lte=timezone.now(),
    ).order_by("address__region", "name", "start_date")

    family = None
    invites = None
    participating = None
    current_activities_with_persons = current_activities
    children = []
    persons = []
    user_region = ""
    persons = []

    if request.user.is_authenticated:
        person = user_to_person(request.user)

        if person:
            # Wonder if we can have the data for the region of the user home location is the first ones ?
            # we have to check for region for the logged on user
            if person.dawa_id == "":
                user_region = ""
            else:
                dawa_req = (
                    f"https://dawa.aws.dk/adresser/{person.dawa_id}?format=geojson"
                )
                try:
                    dawa_reply = json.loads(requests.get(dawa_req).text)
                    user_region = dawa_reply["properties"]["regionsnavn"]
                except Exception:
                    user_region = ""
                    # and we simply skip the region, and sorting will be as default

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
                    for act in ActivityParticipant.objects.filter(
                        person=child["person"].id
                    )
                ]
            persons = [
                {"person": person, "waitinglists": WaitingList.get_by_person(person)}
                for person in family.get_persons()
            ]
            for person in persons:
                person["departments_is_waiting"] = [
                    department for (department, _place) in person["waitinglists"]
                ]
                person["participating_activities"] = [
                    (act.activity.id)
                    for act in ActivityParticipant.objects.filter(
                        person=person["person"].id
                    )
                ]
            persons = [
                {"person": person, "waitinglists": WaitingList.get_by_person(person)}
                for person in family.get_persons()
            ]
            for person in persons:
                person["departments_is_waiting"] = [
                    department for (department, _place) in person["waitinglists"]
                ]
                person["participating_activities"] = [
                    (act.activity.id)
                    for act in ActivityParticipant.objects.filter(
                        person=person["person"].id
                    )
                ]
            invites = ActivityInvite.objects.filter(
                person__family=family,
                expire_dtm__gte=timezone.now(),
                rejected_at=None,
                person__anonymized=False,
            )
            participating = ActivityParticipant.objects.filter(
                person__family=family,
                activity__activitytype__in=["FORLØB", "ARRANGEMENT"],
                person__anonymized=False,
            ).order_by("-activity__start_date")

            current_activities_with_persons = []
            # augment open invites with the persons who could join it in the family
            activities_for_region_of_user = []
            activities_for_other_regions = []
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
                    a = {
                        "id": curActivity.id,
                        "name": curActivity.name,
                        "open_invite": curActivity.open_invite,
                        "department": curActivity.department,
                        "persons": applicablePersons,
                        "min_age": curActivity.min_age,
                        "max_age": curActivity.max_age,
                        "start_date": curActivity.start_date,
                        "end_date": curActivity.end_date,
                        "signup_closing": curActivity.signup_closing,
                        "userregion": user_region,
                        "address": curActivity.address,
                        "seats_left": curActivity.seats_left(),
                    }
                    if curActivity.address.region == user_region:
                        activities_for_region_of_user.append(a)
                    else:
                        activities_for_other_regions.append(a)
            current_activities_with_persons = (
                activities_for_region_of_user + activities_for_other_regions
            )

    context = {
        "family": family,
        "invites": invites,
        "participating": participating,
        "current_activities": current_activities_with_persons,
        "children": children,
        "persons": persons,
    }
    return render(request, "members/activities.html", context)

from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone

from members.models.activity import Activity

from members.models.activityparticipant import ActivityParticipant
from members.models import Person
from members.utils.user import user_to_person
from members.utils.user import user_to_family

from django.contrib.auth.decorators import user_passes_test
from members.utils.user import is_not_logged_in_and_has_person

import requests
import json


@user_passes_test(is_not_logged_in_and_has_person, "/admin_signup/")
def Membership(request):
    current_activities = Activity.objects.filter(
        signup_closing__gte=timezone.now(),
        activitytype__in=["FORENINGSMEDLEMSKAB"],
    ).order_by("start_date")

    family = None
    participating = None
    membership_activities_with_persons = current_activities
    if request.user.is_authenticated:
        person = user_to_person(request.user)

        if person:
            # Wonder if we can have the data for the region of the user home location is the first ones ?
            # we have to check for region for the logged on user
            dawa_req = f"https://dawa.aws.dk/adresser/{person.dawa_id}?format=geojson"
            try:
                dawa_reply = json.loads(requests.get(dawa_req).text)
                user_region = dawa_reply["properties"]["regionsnavn"]
            except Exception:
                user_region = ""
                # and we simply skip the region, and sorting will be as default

            family = user_to_family(request.user)
            participating = ActivityParticipant.objects.filter(
                member__person__family=family,
                activity__activitytype__in=["FORENINGSMEDLEMSKAB"],
            ).order_by("-activity__start_date")

            membership_activities_with_persons = []
            membershiP_activities_for_region_of_user = []
            membership_activities_for_other_regions = []
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
                    a = {
                        "id": curActivity.id,
                        "name": curActivity.name,
                        "union": curActivity.union,
                        "persons": applicablePersons,
                        "department": curActivity.department,
                        "streetname": curActivity.streetname,
                        "housenumber": curActivity.housenumber,
                        "floor": curActivity.floor,
                        "door": curActivity.door,
                        "zipcode": curActivity.zipcode,
                        "city": curActivity.city,
                        "price": curActivity.price_in_dkk,
                        "start_date": curActivity.start_date,
                        "end_date": curActivity.end_date,
                    }

                    if curActivity.union.address.region == user_region:
                        membershiP_activities_for_region_of_user.append(a)
                    else:
                        membership_activities_for_other_regions.append(a)
                membership_activities_with_persons = (
                    membershiP_activities_for_region_of_user
                    + membership_activities_for_other_regions
                )

    context = {
        "family": family,
        "participating": participating,
        "current_activities": membership_activities_with_persons,
    }
    return render(request, "members/membership.html", context)

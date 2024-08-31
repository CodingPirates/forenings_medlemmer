from datetime import date
from django.shortcuts import render
from django.utils import timezone

from members.models.activity import Activity

from members.models.activityparticipant import ActivityParticipant
from members.models.member import Member
from members.models.person import Person
from members.models.union import Union
from members.utils.user import user_to_person
from members.utils.user import user_to_family

from django.contrib.auth.decorators import user_passes_test
from members.utils.user import is_not_logged_in_and_has_person
from members.utils.dawa_data import get_user_region


@user_passes_test(is_not_logged_in_and_has_person, "/admin_signup/")
def Membership(request):
    unions = Union.objects.filter(
        closed_at=None,
        founded_at__lte=timezone.now(),
    ).order_by("address__region", "-name", "founded_at")

    family = None
    members = None
    memberships_with_persons = unions
    if request.user.is_authenticated:
        person = user_to_person(request.user)

        if person:
            user_region = get_user_region(person) if person.dawa_id != "" else None

            family = user_to_family(request.user)
            members = Member.objects.filter(
                person__family=family,
            ).order_by("-member_since")

            memberships_with_persons = []
            memberships_for_region_of_user = []
            memberships_for_other_regions = []
            # augment open invites with the persons who could join it in the family
            for union in unions:
                applicablePersons = Person.objects.filter(
                    family=family,  # only members of this family
                )

                if applicablePersons.exists():
                    a = {
                        "id": union.id,
                        "name": union.name,
                        "persons": applicablePersons,
                        "address": union.address,
                        "membership_price_in_dkk": union.membership_price_in_dkk,
                        "start_date": date(date.today().year, 1, 1),
                        "end_date": date(date.today().year, 12, 31),
                    }

                    if union.address.region == user_region:
                        memberships_for_region_of_user.append(a)
                    else:
                        memberships_for_other_regions.append(a)
                memberships_with_persons = (
                    memberships_for_region_of_user
                    + memberships_for_other_regions
                )

    context = {
        "family": family,
        "members": members,
        "memberships_available": memberships_with_persons,
    }
    return render(request, "members/membership.html", context)

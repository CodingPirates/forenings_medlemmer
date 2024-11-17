import datetime
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

from members.models.person import Person
from members.utils.user import user_to_person, has_user
from members.views.UnacceptedInvitations import get_unaccepted_invitations_for_family


@login_required
@user_passes_test(has_user, "/admin_signup/")
def FamilyDetails(request):
    family = user_to_person(request.user).family

    # update visited field
    family.last_visit_dtm = timezone.now()
    family.save()

    need_confirmation = family.confirmed_at is None or (
        family.confirmed_at
        < timezone.now()
        - datetime.timedelta(days=settings.REQUEST_FAMILY_VALIDATION_PERIOD)
    )
    unaccepted_invitations = get_unaccepted_invitations_for_family(family)

    context = {
        "family": family,
        "need_confirmation": need_confirmation,
        "children": family.person_set.filter(membertype=Person.CHILD),
        "request_parents": family.person_set.exclude(membertype=Person.CHILD).count()
        < 1,
        "ordered_persons": family.person_set.order_by("membertype").all(),
        "invites": unaccepted_invitations,
    }
    return render(request, "members/family_details.html", context)

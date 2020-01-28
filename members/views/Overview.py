import datetime
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models.department import Department
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.utils.user import user_to_person, has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def Overview(request):
    family = user_to_person(request.user).family
    invites = ActivityInvite.objects.filter(
        person__family=family, expire_dtm__gte=timezone.now(), rejected_dtm=None
    )

    context = {
        "invites": invites,
    }
    return render(request, "members/overview.html", context)

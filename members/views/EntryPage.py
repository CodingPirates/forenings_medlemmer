from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render
from django.utils import timezone

from members.models.activityinvite import ActivityInvite
from members.utils.user import user_to_person


@xframe_options_exempt
def EntryPage(request):
    if not request.user.is_anonymous:
        user = user_to_person(request.user)
        if user is None:
            # e.g. if logged in as admin
            context = {}
        else:
            family = user.family
            invites = ActivityInvite.objects.filter(
                person__family=family, expire_dtm__gte=timezone.now(), rejected_dtm=None
            )

            context = {
                "invites": invites,
            }
    else:
        context = {}

    return render(request, "members/entry_page.html", context)

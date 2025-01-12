from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render

from members.utils.user import user_to_person
from members.views.UnacceptedInvitations import get_unaccepted_invitations_for_family


@xframe_options_exempt
def EntryPage(request):
    if not request.user.is_anonymous:
        user = user_to_person(request.user)
        if user is None:
            # e.g. if logged in as admin
            context = {}
        else:
            family = user.family
            unaccepted_invitations = get_unaccepted_invitations_for_family(family)
            context = {
                "invites": unaccepted_invitations,
            }
    else:
        context = {}

    return render(request, "members/entry_page.html", context)

from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render

from members.models.activityparticipant import ActivityParticipant
from members.utils.user import user_to_person
from members.views.UnacceptedInvitations import get_unaccepted_invitations_for_family


@xframe_options_exempt
def EntryPage(request):
    show_slack_menu = False
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.has_perm(
            "members.can_approve_slack_invites"
        ):
            show_slack_menu = True
    if not request.user.is_anonymous:
        user = user_to_person(request.user)
        if user is None:
            # e.g. if logged in as admin
            context = {"show_slack_menu": show_slack_menu}
        else:
            family = user.family
            unaccepted_invitations = get_unaccepted_invitations_for_family(family)
            missing_payments = ActivityParticipant.get_missing_payments_for_family(
                family
            )
            context = {
                "missing_payments": missing_payments,
                "invites": unaccepted_invitations,
                "show_slack_menu": show_slack_menu,
            }
    else:
        context = {"show_slack_menu": show_slack_menu}

    return render(request, "members/entry_page.html", context)

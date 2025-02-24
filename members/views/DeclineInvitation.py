import uuid
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from members.forms import ActivivtyInviteDeclineForm
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant


def DeclineInvitation(request, unique, invitation_id):
    try:
        unique = uuid.UUID(unique)
    except ValueError:
        return HttpResponseBadRequest("Familie id er ugyldigt")
    activity_invite = get_object_or_404(
        ActivityInvite, pk=invitation_id, person__family__unique=unique
    )

    is_participating = ActivityParticipant.objects.filter(
        activity=activity_invite.activity, person=activity_invite.person
    ).exists()

    if request.method == "POST":
        form = ActivivtyInviteDeclineForm(request.POST)
        if form.is_valid():
            if ActivityParticipant.objects.filter(
                activity=activity_invite.activity, person=activity_invite.person
            ).exists():
                return HttpResponseBadRequest(
                    f"'{activity_invite.person}' deltager allerede i '{activity_invite.activity}' og kan ikke afvise invitationen."
                )
            elif activity_invite.rejected_at is not None:
                return HttpResponseBadRequest(
                    f"Invitationen til  {activity_invite.person} for '{activity_invite.activity}' er allerede afvist."
                )
            else:
                activity_invite.rejected_at = timezone.now()
                activity_invite.save()
            return HttpResponseRedirect(reverse("activities"))
    else:
        form = ActivivtyInviteDeclineForm()

    context = {
        "activity_invite": activity_invite,
        "form": form,
        "is_participating": is_participating,
    }
    return render(request, "members/decline_activivty_invite.html", context)

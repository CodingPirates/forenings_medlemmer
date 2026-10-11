from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from members.forms import ActivivtyInviteDeclineForm
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant


def DeclineInvitation(request, decline_uuid, invitation_id):
    activity_invite = get_object_or_404(
        ActivityInvite, pk=invitation_id, decline_uuid=decline_uuid
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
                activity_invite.decline_reason = form.cleaned_data["decline_reason"]
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

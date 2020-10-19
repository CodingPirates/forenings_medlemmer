import uuid

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from members.forms import ActivivtyInviteDeclineForm
from members.models.activityinvite import ActivityInvite


def DeclineInvitation(request, unique, invitation_id):
    try:
        unique = uuid.UUID(unique)
    except ValueError:
        return HttpResponseBadRequest("Familie id er ugyldigt")
    activity_invite = get_object_or_404(
        ActivityInvite, pk=invitation_id, person__family__unique=unique
    )

    if request.method == "POST":
        form = ActivivtyInviteDeclineForm(request.POST)
        if form.is_valid():
            activity_invite.rejected_dtm = timezone.now()
            activity_invite.save()
            return HttpResponseRedirect(reverse("activities"))
    else:
        form = ActivivtyInviteDeclineForm()

    context = {"activity_invite": activity_invite, "form": form}
    return render(request, "members/decline_activivty_invite.html", context)

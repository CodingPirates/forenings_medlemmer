import uuid
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from members.forms import ActivivtyInviteDeclineForm
from members.models.activityinvite import ActivityInvite


@login_required
def DeclineInvitation(request, invitation_id):
    unique = user_to_person(request.user).family.unique
    activity_invite = get_object_or_404(ActivityInvite, pk=invitation_id, person__family__unique=unique)

    if(request.method == 'POST'):
        form = ActivivtyInviteDeclineForm(request.POST)
        if form.is_valid():
            activity_invite.rejected_dtm = timezone.now()
            activity_invite.save()
            return HttpResponseRedirect(reverse('family_detail', args=[activity_invite.person.family.unique]))
    else:
        form = ActivivtyInviteDeclineForm()

    context = {
        'activity_invite': activity_invite,
        'form': form
    }
    return render(request, 'members/decline_activivty_invite.html', context)

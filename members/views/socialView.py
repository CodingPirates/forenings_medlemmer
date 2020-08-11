from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from members.utils.user import user_to_person, has_user
from members.models.volunteer import Volunteer


@login_required
@user_passes_test(has_user, "/admin_signup/")
def socialView(request):
    person = user_to_person(request.user)
    volunteer = False
    if Volunteer.objects.filter(person=person).count() > 0:
        volunteer = True
    return render(request, "members/social_view.html", {"volunteer": volunteer})

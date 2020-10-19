from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.utils.user import has_user, user_to_person


@login_required
@user_passes_test(has_user, "/admin_signup/")
def ConfirmFamily(request):
    family = user_to_person(request.user).family
    persons = Person.objects.filter(family=family)
    subscribed_waiting_lists = WaitingList.objects.filter(person__family=family)

    if request.method == "POST":
        """ No data recieved - just set confirmed_dtm date to now """
        family.confirmed_dtm = timezone.now()
        family.save()
        return HttpResponseRedirect(reverse("family_detail"))
    else:
        context = {
            "family": family,
            "persons": persons,
            "subscribed_waitinglists": subscribed_waiting_lists,
        }
        return render(request, "members/family_confirm_details.html", context)

from django.shortcuts import render

from members.models.waitinglist import WaitingList
from django.contrib.auth.decorators import login_required, user_passes_test

from members.utils.user import user_to_person, has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def waitinglistView(request):
    family = user_to_person(request.user).family
    children = family.get_children()
    data = [
        {"person": child, "waitinglists": WaitingList.get_by_child(child)}
        for child in children
    ]
    return render(request, "members/waitinglist.html", {"children": data})

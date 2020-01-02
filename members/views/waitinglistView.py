from django.shortcuts import render

from members.models.waitinglist import WaitingList
from django.contrib.auth.decorators import login_required


@login_required
def waitinglistView(request):
    family = user_to_person(request.user).family
    children = family.get_children()
    data = [
        {"person": child, "waitinglists": WaitingList.get_by_child(child)}
        for child in children
    ]
    return render(request, "members/waitinglist.html", {"children": data})

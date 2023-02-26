from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from members.models.department import Department
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.utils.user import user_to_person, has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def WaitingListSetSubscription(request, id, departmentId, action):
    family = user_to_person(request.user).family
    person = get_object_or_404(Person, pk=id)

    if person.family.id != family.id:
        raise Http404("Person ikke i samme familie som bruger")
    department = get_object_or_404(Department, pk=departmentId)

    if action == "subscribe":
        if WaitingList.objects.filter(person=person, department=department):
            raise Http404(
                "{} er allerede på {}s venteliste".format(person.name, department.name)
            )
        waiting_list = WaitingList()
        waiting_list.person = person
        waiting_list.department = department
        waiting_list.save()

    if action == "unsubscribe":
        try:
            waiting_list = WaitingList.objects.get(person=person, department=department)
            waiting_list.delete()
        except Exception:
            raise Http404(
                "{} er ikke på {}s venteliste".format(person.name, department.name)
            )

    return HttpResponseRedirect(reverse("department_signup"))

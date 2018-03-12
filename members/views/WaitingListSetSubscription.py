import uuid

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from members.models.department import Department
from members.models.person import Person
from members.models.waitinglist import WaitingList

def WaitingListSetSubscription(request, unique, id, departmentId, action):
    try:
        unique = uuid.UUID(unique)
    except ValueError:
        return HttpResponseBadRequest("Familie id er ugyldigt")

    person = get_object_or_404(Person, pk=id)
    if person.family.unique != unique:
        raise Http404("Person eksisterer ikke")
    department = get_object_or_404(Department,pk=departmentId)

    if action == 'subscribe':
        print('subscribing')
        if WaitingList.objects.filter(person = person, department = department):
            raise Http404("{} er allerede på {}s venteliste".format(person.name,department.name))
        waiting_list = WaitingList()
        waiting_list.person = person
        waiting_list.department = department
        waiting_list.save()

    if action == 'unsubscribe':
        print('un-subscribing')
        try:
            waiting_list = WaitingList.objects.get(person = person, department = department)
            waiting_list.delete()
        except:
            raise Http404("{} er ikke på {}s venteliste".format(person.name,department.name))

    return HttpResponseRedirect(reverse('family_detail', args=[unique]))

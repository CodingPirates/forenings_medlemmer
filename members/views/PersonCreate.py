import uuid

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from members.forms import PersonForm
from members.models.family import Family
from members.models.person import Person

from members.views.UpdatePersonFromForm import UpdatePersonFromForm


@login_required
def PersonCreate(request, membertype):
    family = user_to_person(request.user).family
    if request.method == 'POST':
        person = Person()
        person.membertype = membertype
        person.family = family
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            UpdatePersonFromForm(person,form)
            return HttpResponseRedirect(reverse('family_detail'))
    else:
        person = Person()
        person.membertype = membertype
        if family.person_set.count() > 0 :
            first_person = family.person_set.first()
            person.family = family
            person.zipcode = first_person.zipcode
            person.city = first_person.city
            person.streetname = first_person.streetname
            person.housenumber = first_person.housenumber
            person.floor = first_person.floor
            person.door = first_person.door
            person.placename = first_person.placename
            person.dawa_id = first_person.dawa_id
        form = PersonForm(instance=person)
    return render(request, 'members/person_create_or_update.html', {'form': form, 'person' : person, 'family': family, 'membertype': membertype})

import uuid

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from members.forms import PersonForm
from members.models.person import Person

from members.views.UpdatePersonFromForm import UpdatePersonFromForm


@login_required
def PersonUpdate(request, id):
    person = user_to_person(request.user)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            UpdatePersonFromForm(person,form)
            return HttpResponseRedirect(reverse('family_detail', args=[person.family.unique]))
    else:
        form = PersonForm(instance=person)
    return render(request, 'members/person_create_or_update.html', {'form': form, 'person': person})


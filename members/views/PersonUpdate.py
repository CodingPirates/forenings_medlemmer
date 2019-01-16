from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from members.forms import PersonForm

from members.views.UpdatePersonFromForm import UpdatePersonFromForm

from members.utils.user import user_to_person


@login_required
def PersonUpdate(request, id):
    person = user_to_person(request.user)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            UpdatePersonFromForm(person, form)
            return HttpResponseRedirect(reverse('family_detail'))
    else:
        form = PersonForm(instance=person)
    return render(request, 'members/person_create_or_update.html', {'form': form, 'person': person})

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from members.models import Person, Family
from members.forms import PersonForm

class FamilyCreate(CreateView):
    model=Family
    fieds=['email']
    def get_success_url(self):
        return '../family/{}/'.format(self.object.unique)

def Details(request,unique):
    family = get_object_or_404(Family, unique=unique)
    context = {
        'family': family
    }
    return render(request, 'members/details.html', context)

def UpdatePersonFromForm(person, form):
    person.name = form.cleaned_data['name']
    person.street = form.cleaned_data['street']
    person.zipcity = form.cleaned_data['zipcity']
    person.on_waiting_list = form.cleaned_data['on_waiting_list']
    person.membertype = form.cleaned_data['membertype']
    person.email = form.cleaned_data['email']
    person.phone = form.cleaned_data['phone']
    person.save()

def PersonCreate(request, unique):
    family = get_object_or_404(Family, unique=unique)
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = Person()
            person.family = family
            UpdatePersonFromForm(person,form)
            return HttpResponseRedirect(reverse('family_detail', args=[family.unique]))
    else:
        form = PersonForm()
    return render(request, 'members/person_create.html', {'form': form, 'family': family})

def PersonUpdate(request, unique, id):
    person = get_object_or_404(Person, pk=id)
    if person.family.unique != unique:
        raise Http404("Person eksisterer ikke")
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            UpdatePersonFromForm(person,form)
            return HttpResponseRedirect(reverse('family_detail', args=[person.family.unique]))
    else:
        form = PersonForm(instance=person)
    return render(request, 'members/person_update.html', {'form': form, 'person': person})

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
from django.http import Http404
from members.models import Person, Family

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

class PersonCreate(CreateView):
    model=Person
    def get_object(self):
        family = get_object_or_404(Family, unique=self.kwargs['unique'])
        person = Person()
        person.family = family
        return person
    def get_success_url(self):
        return '../family/{}/'.format(self.object.family.unique)

class PersonUpdate(UpdateView):
    model=Person
    def get_object(self):
        person = get_object_or_404(Person, pk=self.kwargs['pk'])
        if person.family.unique != self.kwargs['unique']:
            raise Http404("Person does not exist")
        return person
    def get_success_url(self):
        return '../family/{}/'.format(self.object.family.unique)

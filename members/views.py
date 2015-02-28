from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
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

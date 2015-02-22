from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from members.models import Person, Family

class FamilyCreate(CreateView):
    model=Family
    fieds=['email']

class FamilyUpdate(UpdateView):
    fields=['email']
    def get_object(self):
        return get_object_or_404(Family, unique=self.kwargs['pk'])

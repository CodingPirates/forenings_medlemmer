from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from members.models import Person, Family, ActivityInvite, ActivityParticipant, Member, Activity
from members.forms import PersonForm
import datetime

class FamilyCreate(CreateView):
    model=Family
    fieds=['email']
    def get_success_url(self):
        return reverse('family_detail', args=[self.object.unique])

def Details(request,unique):
    family = get_object_or_404(Family, unique=unique)
    invites= ActivityInvite.objects.filter(person__family = family)
    currents = ActivityParticipant.objects.filter(member__person__family = family).order_by('-activity__start_date')
    context = {
        'family': family,
        'invites': invites,
        'currents': currents
    }
    return render(request, 'members/details.html', context)

def DeclineInvitation(request, unique):
    activity_invite = get_object_or_404(ActivityInvite, unique=unique)
    activity_invite.delete()
    return HttpResponseRedirect(reverse('family_detail', args=[activity_invite.person.family.unique]))

def AcceptInvitation(request, unique):
    activity_invite = get_object_or_404(ActivityInvite, unique=unique)
    person = activity_invite.person
    person.on_waiting_list = False
    person.save()
    try:
        member = Member.objects.get(person=person,department=activity_invite.activity.department)
    except Member.DoesNotExist:
        member = Member()
        member.person = person
        member.department = activity_invite.activity.department
        member.save()
    acticity_participant = ActivityParticipant()
    acticity_participant.member = member
    acticity_participant.activity = activity_invite.activity
    acticity_participant.save()
    activity_invite.delete()
    return HttpResponseRedirect(reverse('family_detail', args=[activity_invite.person.family.unique]))

def UpdatePersonFromForm(person, form):
    person.name = form.cleaned_data['name']
    person.street = form.cleaned_data['street']
    person.zipcity = form.cleaned_data['zipcity']
    person.on_waiting_list = form.cleaned_data['on_waiting_list']
    person.email = form.cleaned_data['email']
    person.phone = form.cleaned_data['phone']
    person.save()

def PersonCreate(request, unique, membertype):
    family = get_object_or_404(Family, unique=unique)
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = Person()
            person.membertype = membertype
            person.family = family
            UpdatePersonFromForm(person,form)
            return HttpResponseRedirect(reverse('family_detail', args=[family.unique]))
    else:
        form = PersonForm()
    return render(request, 'members/person_create.html', {'form': form, 'family': family, 'membertype': membertype})

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

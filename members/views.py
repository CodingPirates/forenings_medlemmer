from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from members.models import Person, Family, ActivityInvite, ActivityParticipant, Member, Activity, EmailTemplate
from members.forms import PersonForm, getLoginForm, signupForm
import datetime

class FamilyCreate(CreateView):
    model=Family
    fields=['email']
    def get_success_url(self):
        return reverse('family_detail', args=[self.object.unique])

def FamilyDetails(request,unique):
    family = get_object_or_404(Family, unique=unique)
    invites= ActivityInvite.objects.filter(person__family = family)
    currents = ActivityParticipant.objects.filter(member__person__family = family).order_by('-activity__start_date')
    context = {
        'family': family,
        'invites': invites,
        'currents': currents
    }
    return render(request, 'members/family_details.html', context)
def InviteDetails(request, unique):
    activity_invite = get_object_or_404(ActivityInvite, unique=unique)
    context = {
        'invite': activity_invite
    }
    return render(request, 'members/activity_invite_details.html',context)

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
    person.city = form.cleaned_data['city']
    person.zipcode = form.cleaned_data['zipcode']
    person.streetname = form.cleaned_data['streetname']
    person.housenumber = form.cleaned_data['housenumber']
    person.floor = form.cleaned_data['floor']
    person.door = form.cleaned_data['door']
    person.placename = form.cleaned_data['placename']
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
        person = Person()
        if family.person_set.count() > 0 :
            person.zipcode = family.person_set.first().zipcode
            person.streetname = family.person_set.first().streetname
            person.housenumber = family.person_set.first().housenumber
            person.floor = family.person_set.first().floor
            person.door = family.person_set.first().door
            person.placename = family.person_set.first().placename
        form = PersonForm(instance=person)
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

def EntryPage(request):
    if request.method == 'POST':
        # figure out which form was filled out.
        if request.POST['form_id'] == 'signup':
            # signup has been filled
            getLogin = getLoginForm()
            signup = signupForm(request.POST)
            if signup.is_valid():
                # check if family already exists
                try:
                    family = Family.objects.get(email=request.POST['parent_email'])
                    # family was already created - we can't create this family again
                    signup.add_error('parent_email', 'denne email adresse er allerede oprettet. Benyt "Ret indtastning" for at få gensendt et link.')
                    return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup, 'sendEmail' : False})
                except:
                    # all is fine - we did not expect any
                    pass
                #create new family.
                family = Family.objects.create(email = signup.cleaned_data['parent_email'])
                family.save()

                #create parent
                parent = Person.objects.create(membertype = Person.PARENT,
                    name = signup.cleaned_data['parent_name'],
                    zipcode = signup.cleaned_data['zipcode'],
                    city = signup.cleaned_data['city'],
                    streetname = signup.cleaned_data['streetname'],
                    housenumber = signup.cleaned_data['housenumber'],
                    floor = signup.cleaned_data['floor'],
                    door = signup.cleaned_data['door'],
                    dawa_id = signup.cleaned_data['dawa_id'],
                    placename = signup.cleaned_data['placename'],
                    email = signup.cleaned_data['parent_email'],
                    phone = signup.cleaned_data['parent_phone'],
                    family = family
                    )
                parent.save()

                #create child
                child = Person.objects.create(membertype = Person.CHILD,
                    name = signup.cleaned_data['child_name'],
                    zipcode = signup.cleaned_data['zipcode'],
                    city = signup.cleaned_data['city'],
                    streetname = signup.cleaned_data['streetname'],
                    housenumber = signup.cleaned_data['housenumber'],
                    floor = signup.cleaned_data['floor'],
                    door = signup.cleaned_data['door'],
                    dawa_id = signup.cleaned_data['dawa_id'],
                    placename = signup.cleaned_data['placename'],
                    email = signup.cleaned_data['child_email'],
                    phone = signup.cleaned_data['child_phone'],
                    birthday = signup.cleaned_data['child_birthday'],
                    family = family
                    )
                child.save()

                # send email with login link
                EmailTemplate.objects.get(idname = 'LINK').makeEmail(family, {})

                #redirect to success
                return HttpResponseRedirect(reverse('login_email_sent'))
            else:
                getLogin = getLoginForm()
                return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup, 'sendEmail' : False})

        elif request.POST['form_id'] == 'getlogin':
            # just resend email
            signup = signupForm()
            getLogin = getLoginForm(request.POST)
            if getLogin.is_valid():
                # find family
                try:
                    family = Family.objects.get(email=getLogin.cleaned_data['email'])
                    # send email to user
                    EmailTemplate.objects.get(idname = 'LINK').makeEmail(family, {})
                    return HttpResponseRedirect(reverse('login_email_sent'))

                except Family.DoesNotExist:
                    getLogin.add_error('email', 'Denne addresse er ikke kendt i systemet. Hvis du er sikker på du er oprettet, så check adressen, eller opret dig via tilmeldings formularen først.')

            return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup})

    # initial load (if we did not return above)
    getLogin = getLoginForm()
    signup = signupForm()
    return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup})

def loginEmailSent(request):
    return render(request, 'members/login_email_sent.html')


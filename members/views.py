from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from members.models import Person, Family, ActivityInvite, ActivityParticipant, Member, Activity, EmailTemplate, Department, WaitingList
from members.forms import PersonForm, getLoginForm, signupForm
from django.utils import timezone
from django.conf import settings
import datetime

def FamilyDetails(request,unique):
    family = get_object_or_404(Family, unique=unique)
    invites= ActivityInvite.objects.filter(person__family = family)
    open_activities = Activity.objects.filter(open_invite = True)
    participating = ActivityParticipant.objects.filter(member__person__family = family).order_by('-activity__start_date')
    departments_with_no_waiting_list = Department.objects.filter(has_waiting_list = False)
    waiting_lists = WaitingList.objects.filter(person__family = family)
    children = family.person_set.filter(membertype = Person.CHILD)

    #update visited field
    family.last_visit_dtm = timezone.now()
    family.save()

    department_children_waiting = {'departments': {}}
    for department in Department.objects.filter(has_waiting_list = True):
        department_children_waiting['departments'][department.pk] = {}
        department_children_waiting['departments'][department.pk]['object'] = department
        department_children_waiting['departments'][department.pk]['children_status'] = {}
        for child in children:
            department_children_waiting['departments'][department.pk]['children_status'][child.pk] = {}
            department_children_waiting['departments'][department.pk]['children_status'][child.pk]['object'] = child
            department_children_waiting['departments'][department.pk]['children_status'][child.pk]['firstname'] = child.name.partition(' ')[0]
            department_children_waiting['departments'][department.pk]['children_status'][child.pk]['waiting'] = False # default not waiting
            for current_wait in waiting_lists:
                if(current_wait.department == department and current_wait.person == child):
                    #child is waiting on this department
                    department_children_waiting['departments'][department.pk]['children_status'][child.pk]['waiting'] = True
                    break

    context = {
        'family': family,
        'invites': invites,
        'participating': participating,
        'open_activities': open_activities,
        'need_confirmation' : family.confirmed_dtm == None or family.confirmed_dtm < timezone.now() - datetime.timedelta(days=settings.REQUEST_FAMILY_VALIDATION_PERIOD),
        'request_parents' : family.person_set.exclude(membertype=Person.CHILD).count() < 1,
        'department_children_waiting' : department_children_waiting,
        'departments_with_no_waiting_list' : departments_with_no_waiting_list,
        'children': children
    }
    return render(request, 'members/family_details.html', context)

def InviteDetails(request, unique):
    activity_invite = get_object_or_404(ActivityInvite, unique=unique)
    context = {
        'invite': activity_invite
    }
    return render(request, 'members/activity_invite_details.html',context)

def ConfirmFamily(request, unique):
    family = get_object_or_404(Family, unique=unique)
    persons = Person.objects.filter(family=family)
    subscribed_waiting_lists = WaitingList.objects.filter(person__family=family)

    if request.method == 'POST':
        ''' No data recieved - just set confirmed_dtm date to now '''
        family.confirmed_dtm = timezone.now()
        family.save()
        return HttpResponseRedirect(reverse('family_detail', args=[unique]))
    else:
        context = {
            'family':family,
            'persons':persons,
            'subscribed_waitinglists': subscribed_waiting_lists
        }
        return render(request, 'members/family_confirm_details.html',context)

def DeclineInvitation(request, unique):
    activity_invite = get_object_or_404(ActivityInvite, unique=unique)
    activity_invite.delete()
    return HttpResponseRedirect(reverse('family_detail', args=[activity_invite.person.family.unique]))

def WaitingListSetSubscription(request, unique, id, departmentId, action):
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
    # Update person and if selected - relatives

    person.name = form.cleaned_data['name']
    person.email = form.cleaned_data['email']
    person.phone = form.cleaned_data['phone']
    person.birthday = form.cleaned_data['birthday']
    person.city = form.cleaned_data['city']
    person.zipcode = form.cleaned_data['zipcode']
    person.streetname = form.cleaned_data['streetname']
    person.housenumber = form.cleaned_data['housenumber']
    person.floor = form.cleaned_data['floor']
    person.door = form.cleaned_data['door']
    person.placename = form.cleaned_data['placename']
    person.dawa_id = form.cleaned_data['dawa_id']

    person.save()

    if(form.cleaned_data['address_global'] in 'True'):
        relatives = person.family.person_set.all()

        for relative in relatives:
            relative.city = form.cleaned_data['city']
            relative.zipcode = form.cleaned_data['zipcode']
            relative.streetname = form.cleaned_data['streetname']
            relative.housenumber = form.cleaned_data['housenumber']
            relative.floor = form.cleaned_data['floor']
            relative.door = form.cleaned_data['door']
            relative.placename = form.cleaned_data['placename']
            relative.dawa_id = form.cleaned_data['dawa_id']

            relative.save()


def PersonCreate(request, unique, membertype):
    family = get_object_or_404(Family, unique=unique)
    if request.method == 'POST':
        person = Person()
        person.membertype = membertype
        person.family = family
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            UpdatePersonFromForm(person,form)
            return HttpResponseRedirect(reverse('family_detail', args=[family.unique]))
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
    return render(request, 'members/person_create.html', {'form': form, 'person' : person, 'family': family, 'membertype': membertype})

def PersonUpdate(request, unique, id):
    person = get_object_or_404(Person, pk=id)
    if person.family.unique != unique:
        raise Http404("Person eksisterer ikke")
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
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
                    return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup})
                except:
                    # all is fine - we did not expect any
                    pass
                #create new family.
                family = Family.objects.create(email = signup.cleaned_data['parent_email'])
                family.confirmed_dtm = timezone.now()
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
                    gender = signup.cleaned_data['child_gender'],
                    family = family
                    )
                child.save()

                # send email with login link
                EmailTemplate.objects.get(idname = 'LINK').makeEmail(family, {})

                #redirect to success
                return HttpResponseRedirect(reverse('login_email_sent'))
            else:
                getLogin = getLoginForm()
                return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup})

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

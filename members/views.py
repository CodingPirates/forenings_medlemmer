from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from members.models import Person, Family, ActivityInvite, ActivityParticipant, Member, Activity, EmailTemplate, Department, WaitingList, QuickpayTransaction, Payment
from members.forms import PersonForm, getLoginForm, signupForm, ActivitySignupForm, ActivivtyInviteDeclineForm
from django.utils import timezone
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
import datetime
import hashlib, hmac
import json

def FamilyDetails(request,unique):
    family = get_object_or_404(Family, unique=unique)
    invites= ActivityInvite.objects.filter(person__family = family, expire_dtm__gte=timezone.now(), rejected_dtm=None)
    open_activities = Activity.objects.filter(open_invite = True, signup_closing__gte=timezone.now()).order_by('zipcode')
    participating = ActivityParticipant.objects.filter(member__person__family = family).order_by('-activity__start_date')
    departments_with_no_waiting_list = Department.objects.filter(has_waiting_list = False)
    waiting_lists = WaitingList.objects.filter(person__family = family)
    children = family.person_set.filter(membertype = Person.CHILD)
    ordered_persons = family.person_set.order_by('membertype').all()

    #update visited field
    family.last_visit_dtm = timezone.now()
    family.save()

    department_children_waiting = {'departments': {}}
    loop_counter=0
    for department in Department.objects.filter(has_waiting_list = True).order_by('zipcode'):
        department_children_waiting['departments'][loop_counter] = {}
        department_children_waiting['departments'][loop_counter]['object'] = department
        department_children_waiting['departments'][loop_counter]['children_status'] = {}
        for child in children:
            department_children_waiting['departments'][loop_counter]['children_status'][child.pk] = {}
            department_children_waiting['departments'][loop_counter]['children_status'][child.pk]['object'] = child
            department_children_waiting['departments'][loop_counter]['children_status'][child.pk]['firstname'] = child.name.partition(' ')[0]
            department_children_waiting['departments'][loop_counter]['children_status'][child.pk]['waiting'] = False # default not waiting
            for current_wait in waiting_lists:
                if(current_wait.department == department and current_wait.person == child):
                    #child is waiting on this department
                    department_children_waiting['departments'][loop_counter]['children_status'][child.pk]['waiting'] = True
                    break
        loop_counter = loop_counter + 1

    context = {
        'family': family,
        'invites': invites,
        'participating': participating,
        'open_activities': open_activities,
        'need_confirmation' : family.confirmed_dtm == None or family.confirmed_dtm < timezone.now() - datetime.timedelta(days=settings.REQUEST_FAMILY_VALIDATION_PERIOD),
        'request_parents' : family.person_set.exclude(membertype=Person.CHILD).count() < 1,
        'department_children_waiting' : department_children_waiting,
        'departments_with_no_waiting_list' : departments_with_no_waiting_list,
        'children': children,
        'ordered_persons' : ordered_persons,
    }
    return render(request, 'members/family_details.html', context)

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

def DeclineInvitation(request, unique, invitation_id):
    activity_invite = get_object_or_404(ActivityInvite, pk=invitation_id, person__family__unique=unique)

    if(request.method == 'POST'):
        form = ActivivtyInviteDeclineForm(request.POST)
        if form.is_valid():
            activity_invite.rejected_dtm=timezone.now()
            activity_invite.save()
            return HttpResponseRedirect(reverse('family_detail', args=[activity_invite.person.family.unique]))
    else:
        form = ActivivtyInviteDeclineForm()

    context = {
                'activity_invite' : activity_invite,
                'form' : form
              }
    return render(request, 'members/decline_activivty_invite.html', context)


def ActivitySignup(request, activity_id, unique=None, person_id=None):
    if(unique is None or person_id is None):
        # View only mode
        view_only_mode = True
    else:
        view_only_mode = False

    activity = get_object_or_404(Activity, pk=activity_id)

    participants = ActivityParticipant.objects.filter(activity=activity).order_by('member__person__name')
    participating = False

    if(request.resolver_match.url_name == 'activity_view_person'):
        view_only_mode = True

    if unique:
        family = get_object_or_404(Family, unique=unique)
    else:
        family = None

    if person_id:
        try:
            person = family.person_set.get(pk=person_id)

            # Check not already signed up
            try:
                participant = ActivityParticipant.objects.get(activity=activity, member__person=person)
                # found - we can only allow one - switch to view mode
                participating = True
                view_only_mode = True
            except ActivityParticipant.DoesNotExist:
                participating = False # this was expected - if not signed up yet

        except Person.DoesNotExist:
            raise Http404('Person not found on family')
    else:
        person = None

    if(not activity.open_invite):
        ''' Make sure valid not expired invitation to event exists '''
        try:
            invitation = ActivityInvite.objects.get(activity=activity, person=person, expire_dtm__gte=timezone.now())
        except ActivityInvite.DoesNotExist:
            view_only_mode = True # not invited - switch to view mode
            invitation = None
    else:
        invitation = None

    # if activity is closed for signup, only invited persons can still join
    if activity.signup_closing < timezone.now().date() and invitation==None:
        view_only_mode = True # Activivty closed for signup

    # check if activity is full
    if activity.seats_left() <= 0:
         view_only_mode = True # activity full

    if(request.method == "POST"):
        if view_only_mode:
            return HttpResponseForbidden('Cannot join this activity now (not invited / signup closed / activity full / already signed up)')

        if activity.max_age < person.age_years() or activity.min_age > person.age_years():
            return HttpResponseForbidden('Barnet skal være mellem ' + str(activity.min_age) + ' og ' + str(activity.max_age) + ' år gammel for at deltage. (Er fødselsdatoen udfyldt korrekt ?)')

        if Person.objects.filter(family=family).exclude(membertype=Person.CHILD).count() <=0:
            return HttpResponseForbidden('Barnet skal have en forælder eller værge. Gå tilbage og tilføj en før du tilmelder.')

        signup_form = ActivitySignupForm(request.POST)

        if signup_form.is_valid():
            # Sign up and redirect to payment link or family page

            # Calculate membership
            membership_start = timezone.datetime(year=activity.start_date.year, month=1, day=1)
            membership_end = timezone.datetime(year=activity.start_date.year, month=12, day=31)
            # check if person is member, otherwise make a member
            try:
                member = Member.objects.get(person=person)
            except Member.DoesNotExist:
                member = Member(
                    department = activity.department,
                    person=person,
                    member_since=membership_start,
                    member_until=membership_end,
                    )
                member.save()

            # update membership end date
            member.member_until=membership_end
            member.save()

            # Make ActivityParticipant
            participant = ActivityParticipant(member=member, activity=activity, note=signup_form.cleaned_data['note'])

            # update photo permission and contact open info
            participant.photo_permission = True # signup_form.cleaned_data['photo_permission']
            participant.contact_visible = signup_form.cleaned_data['address_permission'] == "YES"
            participant.save()

            return_link_url = reverse('activity_view_person', args=[family.unique, activity.id, person.id])

            # Make payment if activity costs
            if activity.price is not None and activity.price != 0:
                # using creditcard ?
                if signup_form.cleaned_data['payment_option'] == Payment.CREDITCARD:
                    payment = Payment(
                        payment_type = Payment.CREDITCARD,
                        activity=activity,
                        activityparticipant=participant,
                        person=person,
                        family=family,
                        body_text=timezone.now().strftime("%Y-%m-%d") + ' Betaling for ' + activity.name + ' på ' + activity.department.name,
                        amount_ore = activity.price,
                    )
                    payment.save()

                    return_link_url = payment.get_quickpaytransaction().get_link_url(return_url = settings.BASE_URL + reverse('activity_view_person', args=[family.unique, activity.id, person.id]))


            # expire invitation
            if invitation:
                invitation.expire_dtm=timezone.now() - timezone.timedelta(days=1)
                invitation.save()

            # reject all seasonal invitations on person if this was a seasonal invite
            # (to avoid signups on multiple departments for club season)
            if activity.is_season():
                invites = ActivityInvite.objects.filter(person=person).exclude(activity=activity)
                for invite in invites:
                    if invite.activity.is_season():
                        invite.rejected_dtm = timezone.now()
                        invite.save()

            return HttpResponseRedirect(return_link_url)
        # fall through else
    else:

        signup_form = ActivitySignupForm()


    context = {
                'family' : family,
                'activity' : activity,
                'person' : person,
                'invitation' : invitation,
                'price' : activity.price / 100,
                'seats_left' : activity.seats_left(),
                'signupform' : signup_form,
                'view_only_mode' : view_only_mode,
                'participating' : participating,
                'participants': participants,
              }
    return render(request, 'members/activity_signup.html', context)

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
    return render(request, 'members/person_create_or_update.html', {'form': form, 'person' : person, 'family': family, 'membertype': membertype})

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
    return render(request, 'members/person_create_or_update.html', {'form': form, 'person': person})

@xframe_options_exempt
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
                    signup.add_error('parent_email', 'Denne email adresse er allerede oprettet. Du kan tilføje flere børn på samme forælder, når du er kommet videre! - Benyt "Gå til min side" ovenfor, for at få gensendt et link hvis du har mistet det')
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
                family.send_link_email()

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
                    family.send_link_email()
                    return HttpResponseRedirect(reverse('login_email_sent'))

                except Family.DoesNotExist:
                    getLogin.add_error('email', 'Denne addresse er ikke kendt i systemet. Hvis du er sikker på du er oprettet, så check adressen, eller opret dig via tilmeldings formularen først.')

            return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup})

    # initial load (if we did not return above)
    getLogin = getLoginForm()
    signup = signupForm()
    return render(request, 'members/entry_page.html', {'loginform' : getLogin, 'signupform' : signup})

@xframe_options_exempt
def loginEmailSent(request):
    return render(request, 'members/login_email_sent.html')

def signQuickpay(base, private_key):
   return hmac.new(private_key, base, hashlib.sha256).hexdigest()

@csrf_exempt
def QuickpayCallback(request):
    checksum = signQuickpay(request.body, bytearray(settings.QUICKPAY_PRIVATE_KEY, 'ascii'))

    #print("comparing checksum: " + request.META['HTTP_QUICKPAY_CHECKSUM_SHA256'] + " (recieved) to: " + checksum + " (calculated)")
    if checksum == request.META['HTTP_QUICKPAY_CHECKSUM_SHA256']:
        # Request is authenticated

        #JSON decode
        callback = json.loads(str(request.body, 'utf8'))

        # We only care about state = processed
        if(callback['state'] != 'processed'):
            HttpResponse('OK') # processing stops here - but tell QuickPay we are OK

        quickpay_transaction = get_object_or_404(QuickpayTransaction, order_id=callback['order_id'])

        if(callback['accepted'] == True):
            quickpay_transaction.payment.set_confirmed()
        else:
            quickpay_transaction.payment.set_rejected(request.body)

        return HttpResponse('OK')
    else:
        # Request is Not authenticated
        return HttpResponseForbidden('Invalid request')

from django.core.urlresolvers import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from members.forms import getLoginForm, signupForm
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
from members.models.family import Family
from members.models.person import Person


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
                # TODO: rewrite this! >>>>
                try:
                    family = Family.objects.get(email__iexact=request.POST['parent_email'])
                    # family was already created - we can't create this family again
                    signup.add_error('parent_email', 'Denne email adresse er allerede oprettet. Du kan tilføje flere børn på samme forælder, når du er kommet videre! - Benyt "Gå til min side" ovenfor, for at få gensendt et link hvis du har mistet det')
                    return render(request, 'members/entry_page.html', {'loginform': getLogin, 'signupform': signup})
                except:
                    # all is fine - we did not expect any
                    pass
                # TODO: rewrite this! <<<<
                # create new family.
                family = Family.objects.create(email=signup.cleaned_data['parent_email'])
                family.confirmed_dtm = timezone.now()
                family.save()

                # create parent
                parent = Person.objects.create(
                    membertype=Person.PARENT,
                    name=signup.cleaned_data['parent_name'],
                    zipcode=signup.cleaned_data['zipcode'],
                    city=signup.cleaned_data['city'],
                    streetname=signup.cleaned_data['streetname'],
                    housenumber=signup.cleaned_data['housenumber'],
                    floor=signup.cleaned_data['floor'],
                    door=signup.cleaned_data['door'],
                    dawa_id=signup.cleaned_data['dawa_id'],
                    placename=signup.cleaned_data['placename'],
                    email=signup.cleaned_data['parent_email'],
                    phone=signup.cleaned_data['parent_phone'],
                    family=family
                )
                parent.save()

                # create child
                child = Person.objects.create(
                    membertype=Person.CHILD,
                    name=signup.cleaned_data['child_name'],
                    zipcode=signup.cleaned_data['zipcode'],
                    city=signup.cleaned_data['city'],
                    streetname=signup.cleaned_data['streetname'],
                    housenumber=signup.cleaned_data['housenumber'],
                    floor=signup.cleaned_data['floor'],
                    door=signup.cleaned_data['door'],
                    dawa_id=signup.cleaned_data['dawa_id'],
                    placename=signup.cleaned_data['placename'],
                    email=signup.cleaned_data['child_email'],
                    phone=signup.cleaned_data['child_phone'],
                    birthday=signup.cleaned_data['child_birthday'],
                    gender=signup.cleaned_data['child_gender'],
                    family=family
                )
                child.save()

                # send email with login link
                family.send_link_email()

                # redirect to success
                return HttpResponseRedirect(reverse('login_email_sent'))
            else:
                getLogin = getLoginForm()
                return render(request, 'members/entry_page.html', {'loginform': getLogin, 'signupform': signup})

        elif request.POST['form_id'] == 'getlogin':
            # just resend email
            signup = signupForm()
            getLogin = getLoginForm(request.POST)
            if getLogin.is_valid():
                # find family
                try:
                    family = Family.objects.get(email=getLogin.cleaned_data['email'])

                    if family.dont_send_mails:
                        getLogin.add_error('email', 'Du har frabedt dig emails fra systemet. Kontakt Coding Pirates direkte.')
                    else:
                        # send email to user
                        family.send_link_email()
                        return HttpResponseRedirect(reverse('login_email_sent'))

                except Family.DoesNotExist:
                    getLogin.add_error('email', 'Denne addresse er ikke kendt i systemet. Hvis du er sikker på du er oprettet, så check adressen, eller opret dig via tilmeldings formularen først.')

            return render(request, 'members/entry_page.html', {'loginform': getLogin, 'signupform': signup})

    # initial load (if we did not return above)
    getLogin = getLoginForm()
    signup = signupForm()
    return render(request, 'members/entry_page.html', {'loginform': getLogin, 'signupform': signup})

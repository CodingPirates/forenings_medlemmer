from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from members.models import PayableItem, Person
from members.utils.user import has_user, user_to_person


@login_required
@user_passes_test(has_user, "/admin_signup/")
def PaymentsView(request):
    logged_in_person = user_to_person(request.user)
    family_members = Person.objects.filter(family=logged_in_person.family)
    payments = PayableItem.objects.filter(person__in=family_members).order_by("-added")
    return render(request, "members/payments.html", {"payments": payments},)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from members.utils.user import user_to_person, has_user
from members.models import Person, PayableItem


@login_required
@user_passes_test(has_user, "/admin_signup/")
def PaymentsView(request):
    logged_in_person = user_to_person(request.user)
    family_members = Person.objects.filter(family=logged_in_person.family)
    payments = PayableItem.objects.filter(person__in=family_members).order_by("-added")
    return render(request, "members/payments_view.html", {"payments": payments},)

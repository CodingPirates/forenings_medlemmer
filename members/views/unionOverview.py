from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from members.models import Union
from members.utils.user import has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def unionOverview(request):
    # get unions
    unions = Union.objects.all()

    return render(request, "members/union_overview.html", {"unions": unions})

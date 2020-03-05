from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from members.models import Union
from members.utils.user import has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def unionMembersView(request, id):
    # get user union
    union = Union.objects.filter(pk=id)
    # get members of union
    members = union[0].members()
    # get years union has been active
    today = timezone.now().date()
    years = range(union[0].founded.year, today.year + 1)

    context = {
        "years": years,
        "current_year": today.year,
        "members": members,
        "union": union[0],
    }

    return render(request, "members/union_members.html", context)

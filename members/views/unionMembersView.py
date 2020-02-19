from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from members.models import Union
from members.utils.user import has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def unionMembersView(request, id):
    # get user union
    union = Union.object.filter(pk=id)
    # get members of union
    members = union.members()
    # get years union has been active
    today = timezone.now().date()
    years = range(union.founded.year, today.year + 1)

    context = {
        "years": years,
        "members": members,
        "union": union,
    }

    return render(request, "members/union_members.html", context)

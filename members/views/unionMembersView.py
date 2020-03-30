from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from members.models import Union
from members.utils.user import has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def unionMembersView(request, union_id):
    # get chosen union
    union = Union.objects.filter(pk=union_id)

    # Check if user is admin of union
    access = Union.user_union_leader(union, request.user)

    # get members of union
    if access is True:
        members = list(set(union[0].members()))

    # get years union has been active
    today = timezone.now().date()
    years = range(union[0].founded.year, today.year + 1)

    context = {
        "years": years,
        "current_year": today.year,
        "members": members,
        "union": union[0],
        "access": access,
    }

    return render(request, "members/union_members.html", context)

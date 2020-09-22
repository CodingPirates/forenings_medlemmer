from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from members.models import Union
from members.utils.user import has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def unionMembersView(request, union_id):
    members = []
    union = get_object_or_404(Union, pk=union_id)

    user_has_access = Union.user_union_leader(union, request.user)

    if user_has_access:
        members = union.members()
    print("Members:")
    print(members)

    today = timezone.now().date()
    years_active = range(union.founded.year, today.year + 1)

    context = {
        "years": years_active,
        "current_year": today.year,
        "members": members,
        "union": union,
        "boardmembers": union.board_members.all(),
        "access": user_has_access,
    }

    return render(request, "members/union_members.html", context)

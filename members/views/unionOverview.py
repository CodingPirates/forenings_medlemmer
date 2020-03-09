from django.shortcuts import render
from members.models import Union


def unionOverview(request):
    return render(
        request, "members/union_overview.html", {"unions": Union.objects.all()}
    )

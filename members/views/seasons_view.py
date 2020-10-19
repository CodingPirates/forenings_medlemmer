from django.shortcuts import render
from members.models import Season


def Seasons(request):
    # TODO finish this
    context = {"seasons": Season.get_open_seasons()}

    return render(request, "members/seasons.html", context)

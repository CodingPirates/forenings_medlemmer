from django.shortcuts import render


def socialView(request):

    return render(request, "members/social_view.html")

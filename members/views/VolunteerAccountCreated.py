from django.shortcuts import render


def VolunteerAccountCreated(request):
    """Success page after volunteer account creation"""
    return render(request, "members/volunteer_account_created.html")

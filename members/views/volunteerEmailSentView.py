from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from members.utils.user import user_to_person, has_user


def volunteerEmailSentView(request):
    return render(request, "members/volunteer_email_sent.html", {"skip_context": True})

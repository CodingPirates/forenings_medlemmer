from django.shortcuts import render


def volunteerEmailSentView(request):
    return render(request, "members/volunteer_email_sent.html", {"skip_context": True})

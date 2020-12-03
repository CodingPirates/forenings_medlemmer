from django.shortcuts import render
from members.models.person import Person
from django.utils import timezone
from members.forms import signupForm


def confirmAge(request):
    if request.method == "POST":
        if request.POST["form_id"] == "signup":
            signup = signupForm(request.POST)
            if signup.is_valid():

                today = timezone.now().date()
                date = signup.cleaned_data["child_birthday"]
                years = (
                    today.year
                    - date.year
                    - ((today.month, today.day) < (date.month, date.day))
                )

                age = years

                context = {
                    "age": age,
                }

                return render(request, "members/confirm_age.html", context)

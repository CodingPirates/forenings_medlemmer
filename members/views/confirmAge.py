from django.shortcuts import render
from members.models.person import Person

def confirmAge(request):


	age = Person.objects.get(
		
		)

	context = {
    	"age": age,
    }

	return render(request, "members/confirm_age.html", context)
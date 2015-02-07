from django.shortcuts import render, get_object_or_404
from members.models import Person
# Create your views here.

def index(request):
    return render(request,'members/index.html',{})

def person(request,person_guid):
    person = get_object_or_404(Person,unique=person_guid)
    return render(request,'members/details.html',{'person':person})

def updateperson(request,person_guid):
    person = get_object_or_404(Person,unique=person_guid)
    return render(request,'members/index.html',{})

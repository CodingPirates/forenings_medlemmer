from django.shortcuts import render, get_object_or_404
from members.models import Person
# Create your views here.

def index(request):
    return render(request,'members/index.html',{})

def person(request,family_guid):
    family = get_object_or_404(Family,unique=family_guid)
    return render(request,'members/details.html',{'family':family, 'persons':family.person_set})

def updateperson(request,family_guid):
    person = get_object_or_404(Family,unique=family_guid)
    return render(request,'members/index.html',{})

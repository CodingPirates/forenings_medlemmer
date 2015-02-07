from django.shortcuts import render
from django.http import HttpResponse
from members.models import Person
# Create your views here.

def index(request):
    return HttpResponse("Hello world")

def person(request,person_guid):
    p = Person.objects.get(unique=person_guid)
    return HttpResponse("You're looking at %s" % p.name)

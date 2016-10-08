from django.core.management.base import BaseCommand, CommandError
from members.models import Department
from django.db import models
import requests, json

class Command(BaseCommand):
    help = "Updates the longtitude and latitude for all departments where it wasn't defined"

    def handle(self, *args, **options):
        deps = Department.objects.filter(models.Q(latitude=None) | models.Q(longtitude=None))
        for dep in deps:
            addressID = 0
            req = 'https://dawa.aws.dk/datavask/adresser?betegnelse=' + dep.addressWithZip().replace(" ", "%20")
            try:
                washed = json.loads(requests.get(req).text)
                addressID = washed['resultater'][0]['adresse']['id']
            except Exception as error:
                print("Couldn't find addressID for " + dep.name)
                print("Error " +  str(error))
            if not(addressID == 0):
                try:
                    req = 'https://dawa.aws.dk/adresser/' + addressID + "?format=geojson"
                    address = json.loads(requests.get(req).text)
                    dep.longtitude =  address['geometry']['coordinates'][0]
                    dep.latitude   =  address['geometry']['coordinates'][1]
                    dep.save()
                    print("Updated coordinates for " + dep.name)
                except Exception as error:
                    print("Couldn't find coordinates for " + dep.name)
                    print("Error " +  str(error))

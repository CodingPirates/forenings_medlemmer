from django.core.management.base import BaseCommand
from members.models.activity import Activity
from members.models.address import Address


class Command(BaseCommand):
    help = "Update all activities, to use Address object"

    def default_value(self, value, defaultvalue):
        if value is None:
            return defaultvalue
        else:
            return value

    def handle(self, *args, **options):
        for activity in Activity.objects.filter(address=None):
            _streetname = self.default_value(activity.streetname, "")
            _housenumber = self.default_value(activity.housenumber, "")
            _floor = self.default_value(activity.floor, "")
            _door = self.default_value(activity.door, "")
            _placename = self.default_value(activity.placename, "")
            _zipcode = self.default_value(activity.zipcode, "")
            _city = self.default_value(activity.city, "")

            # Check for existing address object
            address = Address.objects.filter(
                streetname=_streetname,
                housenumber=_housenumber,
                floor=_floor,
                door=_door,
                placename=_placename,
                zipcode=_zipcode,
                city=_city,
            ).first()
            # If address object found, then update address_id for activity,
            # otherwise: Create new object, and use the new ID
            if address is None:
                address = Address.objects.create(
                    streetname=_streetname,
                    housenumber=_housenumber,
                    floor=_floor,
                    door=_door,
                    placename=_placename,
                    zipcode=_zipcode,
                    city=_city,
                )
                address.save()
            activity.address = address
            activity.save()

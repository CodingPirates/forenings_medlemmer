import requests

from django.core.management.base import BaseCommand
from django.db.models import Q
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
        for activity in Activity.objects.filter(
            Q(address_id=None) | Q(address_id=1)
        ).order_by("-id"):
            _create_new_address = True
            _streetname = self.default_value(activity.streetname, "")
            _housenumber = self.default_value(activity.housenumber, "")
            _floor = self.default_value(activity.floor, "")
            _door = self.default_value(activity.door, "")
            _descriptiontext = self.default_value(activity.placename, "")
            _zipcode = self.default_value(activity.zipcode, "")
            _city = self.default_value(activity.city, "")
            print(
                f"Activity:[{activity.pk}]:[{activity.name}]. Place/descr:[{activity.placename}] descrtxt:[{_descriptiontext}]\r\n"
                ""
            )
            # housenumber, floor and door might be too long (fields in address object is smaller)
            if len(_housenumber) > 5:
                _descriptiontext = f"{_descriptiontext}.*. {_housenumber}"
                _housenumber = ""

            if len(_floor) > 10:
                _descriptiontext = f"{_descriptiontext}.**. {_floor}"
                _floor = ""

            if len(_door) > 5:
                _descriptiontext = f"{_descriptiontext}.***. {_door}"
                _door = ""

            # Check for existing address object
            address = (
                Address.objects.filter(
                    streetname=_streetname,
                    housenumber=_housenumber,
                    floor=_floor,
                    door=_door,
                    zipcode=_zipcode,
                    city=_city,
                )
                .order_by("-id")
                .first()
            )

            # If address object found, then use this object in address_id for the activity,
            print(
                f"  Vej:[{_streetname}] #:[{_housenumber}] Floor:[{_floor}] Dør:[{_door}]. ZIP:[{_zipcode}] By:[{_city}]"
            )

            if address is None:
                # Exact address does not exist, but there might be a record with
                # same DAWA id (e.g. if you searched for "Frode Jakobsens Pl."
                # it's mapped via DAWA to "Frode Jakobsens Plads"

                print("    address is None. Checking Dawa online")
                _dawa_id = ""

                # build text for DAWA request
                text = f"{_streetname} {_housenumber}"
                text = f"{text} {_floor}" if _floor != "" else text
                text = f"{text} {_door}" if _door != "" else text
                # text = f"{text}, {self.placename}" if self.placename != "" else text
                text = f"{text}, {_zipcode} {_city}"

                wash_response = requests.request(
                    "GET",
                    "https://dawa.aws.dk/datavask/adresser",
                    params={"betegnelse": text},
                )
                _category = wash_response.json()["kategori"]
                if wash_response.status_code == 200 and _category != "C":
                    _dawa_id = wash_response.json()["resultater"][0]["adresse"]["id"]

                    print(f"  Checking for existing address w Dawa [{_dawa_id}]")

                    address_check = (
                        Address.objects.filter(
                            dawa_id=_dawa_id,
                        )
                        .order_by("id")
                        .first()
                    )

                    if address_check is not None:
                        activity.address = address_check
                        _dawa_id = address_check.dawa_id
                        _create_new_address = False
                        print(
                            f"    using address_check. dawa=[{address_check.dawa_id}] pk=[{address_check.pk}]"
                        )
                print(f"   _dawa_id = [{_dawa_id}]")
                if _create_new_address:
                    print("     Creating new address")
                    address_new = Address.objects.create(
                        streetname=_streetname,
                        housenumber=_housenumber,
                        floor=_floor,
                        door=_door,
                        descriptiontext=_descriptiontext,
                        zipcode=_zipcode,
                        city=_city,
                    )
                    print(
                        f"    Created new address to match DAWA [{address_new.dawa_id}]"
                    )
                    activity.address = address_new

            else:
                print("    adress exists already !")
                _create_new_address = True
                activity.address = address
            activity.save()

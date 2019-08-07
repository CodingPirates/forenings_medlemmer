from django.test import TestCase

from members.models.address import Address
from members.tests.factories import AddressFactory
from members.utils.address import format_address


class TestModelAddress(TestCase):
    def setUp(self):
        self.address = Address(
            streetname="Prins Jørgens Gård",
            housenumber="1",
            zipcode="1218",
            city="København",
        )
        self.address.save()

    def test_get_housenumber(self):
        address = AddressFactory()
        self.assertGreater(address.housenumber, 0)

    def test_string_address(self):
        address = AddressFactory()
        self.assertEqual(format_address(address.streetname, address.housenumber, address.floor, address.door), str(address))

    def test_get_address_with_zip(self):
        address = AddressFactory()
        self.assertEqual(str(address) + ", " + address.zipcode + " " + address.city, address.addressWithZip())

    def util_calc_distance(self, coord1, coord2):
        # Implements the Haversine formula
        # Ref: https://stackoverflow.com/a/19412565/1689680
        R = 6373.0
        lat1 = math.radians(coord1[0])
        lon1 = math.radians(coord1[1])
        lat2 = math.radians(coord2[0])
        lon2 = math.radians(coord2[1])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def test_update_dawa_data(self):
        self.address.update_dawa_data()
        latLon = "(" + self.address.latitude + ", " + self.address.longitude + ")"
        self.assertLess(
            self.util_calc_distance(
                latLon, (55.67680271, 12.57994743)
            ),
            1.0,  # Calculated distance from the returned value and the expected value can be no more than 1 km
        )
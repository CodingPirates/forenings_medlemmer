from django.test import TestCase

from members.tests.factories import AddressFactory


class TestModelAddress(TestCase):
    def test_get_housenumber(self):
        address = AddressFactory()
        self.assertEqual(int(address.housenumber))
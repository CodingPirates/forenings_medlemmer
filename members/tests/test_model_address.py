from django.test import TestCase

from members.models.address import Address


class TestModelAddress(TestCase):
    def test_address_format(self):
        simple_address = Address(
            streetname="piratvej", housenumber=10, city="København", zipcode="2300"
        )
        appartment_address = Address(
            streetname="Skibgade",
            housenumber=42,
            city="Århus",
            zipcode="7000",
            floor="3",
            door="th",
        )
        row_house_address = Address(
            streetname="Kabys", housenumber=314, city="Århus", zipcode="7000", door="C",
        )
        self.assertEqual(str(simple_address), "piratvej 10, 2300 København")
        self.assertEqual(str(appartment_address), "Skibgade 42 3 th, 7000 Århus")
        self.assertEqual(str(row_house_address), "Kabys 314 C, 7000 Århus")

    def test_fetch_data_by_dawa_id(self):
        home = Address.objects.create(dawa_id="7dd8edbb-370f-4cdf-836c-6b4969a0da9c")
        self.assertEqual(home.streetname, "Sverigesgade")
        self.assertAlmostEqual(home.longitude, 10.38138591)

    def test_fetch_data_by_wash(self):
        home = Address.objects.create(
            streetname="Sverigesgade", housenumber=20, zipcode="5000"
        )
        self.assertEqual(home.dawa_id, "7dd8edbb-370f-4cdf-836c-6b4969a0da9c")

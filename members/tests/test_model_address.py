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
            streetname="Kabys",
            housenumber=314,
            city="Århus",
            zipcode="7000",
            door="C",
        )
        placename_address = Address(
            streetname="Himmelev Bygade",
            housenumber=3,
            city="Roskilde",
            zipcode="4000",
            placename="Himmelev",
        )
        self.assertEqual(str(simple_address), "piratvej 10, 2300 København")
        self.assertEqual(str(appartment_address), "Skibgade 42 3 th, 7000 Århus")
        self.assertEqual(str(row_house_address), "Kabys 314 C, 7000 Århus")
        self.assertEqual(
            str(placename_address), "Himmelev Bygade 3, Himmelev, 4000 Roskilde"
        )

    def test_dawa_overwrite(self):
        home = Address.objects.create(
            ext_address_id="02ba51b3-3482-4c59-be8f-f42bf2b243b6",
            ext_address_overwrite=True,
            latitude=12.591215,
        )
        home.save()
        self.assertEqual(home.latitude, 12.591215)

    def test_fetch_data_by_dawa_id(self):
        home = Address.objects.create(
            ext_address_id="7dd8edbb-370f-4cdf-836c-6b4969a0da9c"
        )
        home.get_ext_address_data()
        self.assertEqual(home.streetname, "Sverigesgade")
        self.assertAlmostEqual(home.longitude, 10.38138591)

    def test_fetch_data_placename(self):
        home = Address.objects.create(
            ext_address_id="0a3f50ab-e8f7-32b8-e044-0003ba298018"
        )
        home.get_ext_address_data()
        self.assertEqual(home.placename, "Himmelev")

    def test_fetch_data_by_wash(self):
        home = Address.objects.create(
            streetname="Sverigesgade", housenumber=20, zipcode="5000"
        )
        home.get_ext_address_data()
        self.assertEqual(home.ext_address_id, "7dd8edbb-370f-4cdf-836c-6b4969a0da9c")

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
            dawa_id="02ba51b3-3482-4c59-be8f-f42bf2b243b6",
            dawa_overwrite=True,
            latitude=12.591215,
        )
        home.save()
        self.assertEqual(home.latitude, 12.591215)

    def test_fetch_data_by_dawa_id(self):
        home = Address.objects.create(dawa_id="7dd8edbb-370f-4cdf-836c-6b4969a0da9c")
        home.get_dawa_data()
        self.assertEqual(home.streetname, "Sverigesgade")
        self.assertAlmostEqual(home.longitude, 10.38138591)

    def test_fetch_data_placename(self):
        home = Address.objects.create(dawa_id="0a3f50ab-e8f7-32b8-e044-0003ba298018")
        home.get_dawa_data()
        self.assertEqual(home.placename, "Himmelev")

    def test_fetch_data_by_wash(self):
        home = Address.objects.create(
            streetname="Sverigesgade", housenumber=20, zipcode="5000"
        )
        home.get_dawa_data()
        self.assertEqual(home.dawa_id, "7dd8edbb-370f-4cdf-836c-6b4969a0da9c")

    def test_get_model_by_dawa_id(self):
        dawa_id = "7dd8edbb-370f-4cdf-836c-6b4969a0da9c"  # CP headquarters

        # No addresses in database yet
        self.assertEqual(Address.objects.all().count(), 0)

        addres = Address.get_by_dawa_id(dawa_id)
        self.assertEqual(addres.zipcode, "5000")  # Got info from dawa
        self.assertEqual(Address.objects.all().count(), 1)

        # Get address again
        addres = Address.get_by_dawa_id(dawa_id)
        # Should still only be one in database
        self.assertEqual(Address.objects.all().count(), 1)

        # Invalid id should give None
        addres = Address.get_by_dawa_id("invalid_id")
        self.assertIsNone(addres)
        self.assertEqual(Address.objects.all().count(), 1)

from django.test import TestCase
from members.models.address import Address
from members.models.emailtemplate import EmailTemplate
import math
from django.core import mail
from members.jobs import EmailSendCronJob


class TestModelAddress(TestCase):
    def setUp(self):
        self.address = Address(
            streetname = "Sverigesgade",
            housenumber = "20",
            floor = "1",
            zipcode = "5000",
            city = "Odense C",
        )
        self.address.save()


    def test_get_housenumber(self):
        sverigesgade = Address.objects.get(streetname="Sverigesgade")
        self.assertEqual(sverigesgade.housenumber, "20")
from django.test import TestCase
from members.models.union import Union
from members.models.department import Department
from members.models.emailtemplate import EmailTemplate
import math


class TestModelDepartment(TestCase):
    def setUp(self):
        self.union = Union()
        self.union.save()

        self.department = Department(
            union=self.union,
            streetname="Prins Jørgens Gård",
            housenumber="1",
            zipcode="1218",
            city="København",
        )
        self.department.save()

        self.emailtemplate = EmailTemplate(
            idname="VOL_NEW",
            name="",
            description="",
            from_address="test@example.com",
            subject="[TEST] new volunteer email",
        )
        self.emailtemplate.save()

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

    def test_get_long_lat(self):
        self.assertLess(
            self.util_calc_distance(
                self.department.getLatLon(), (55.67680271, 12.57994743)
            ),
            1.0,  # Calculated distance from the returned value and the expected value can be no more than 1 km
        )

    # TODO fix this test
    # def test_new_volunteer_email(self):
    #     self.department.new_volunteer_email("")
    #     EmailSendCronJob().do()
    #     self.assertEqual(len(mail.outbox), 1)

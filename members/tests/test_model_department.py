from django.test import TestCase
from members.models.union import Union
from members.models.department import Department


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

    def test_get_long_lat(self):
        self.assertEqual(self.union, self.department.union)
        # TODO make proper tests

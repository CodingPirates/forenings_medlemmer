from django.test import TestCase
from members.models.union import Union
from members.models.department import Department
from members.models.equipment import Equipment
from django.core.exceptions import ValidationError


class TestModelEquipment(TestCase):
    def setUp(self):
        self.union1 = Union(
            name="union1",
            region="S",
            streetname="",
            housenumber="1",
            zipcode="1234",
            city="",
        )
        self.union1.save()

        self.union2 = Union(
            name="union2",
            region="S",
            streetname="",
            housenumber="1",
            zipcode="1234",
            city="",
        )
        self.union2.save()

        self.department = Department(
            name="",
            union=self.union1,
            streetname="",
            housenumber="1",
            zipcode="1234",
            city="",
        )
        self.department.save()

    def test_clean_no_owner(self):
        # Validation should fail if their isn't a owner
        equipment = Equipment()
        with self.assertRaises(ValidationError):
            equipment.clean()
            equipment.save()

    def test_clean_department_owner(self):
        # Test model validation with only department as owner
        equipment = Equipment(department=self.department)
        equipment.clean()
        equipment.save()

    def test_clean_union_owner(self):
        # Test model validation with only union as owner
        equipment = Equipment(union=self.union1)
        equipment.clean()
        equipment.save()

    def test_clean_department_and_union(self):
        # Test the mode validation with both department and union set
        self.department.union = self.union1
        self.department.save()
        equipment = Equipment(union=self.union1, department=self.department)
        # Test validation with department union matching union in equipment
        equipment.clean()
        equipment.save()

        self.department.union = self.union2
        self.department.save()
        # Test validation with department union not matching union in equipment
        with self.assertRaises(ValidationError):
            equipment.clean()
            equipment.save()

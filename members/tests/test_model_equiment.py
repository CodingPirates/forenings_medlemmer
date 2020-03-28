from django.test import TestCase

from members.models.equipment import Equipment
from django.core.exceptions import ValidationError

from .factories import UnionFactory, DepartmentFactory


class TestModelEquipment(TestCase):
    def setUp(self):
        self.union1 = UnionFactory()
        self.union2 = UnionFactory()
        self.department = DepartmentFactory(union=self.union1)

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

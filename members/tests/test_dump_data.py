from django.test import TestCase
from .factories import DepartmentFactory, AddressFactory, UnionFactory
from members.management.commands.dump_public_data import get_dump
from members.models import Department, Union


class TestDumpData(TestCase):
    def setup(self):
        self.departments = DepartmentFactory.create_batch(20)
        self.unions = UnionFactory.create_batch(20)
        self.addresses = AddressFactory.create_batch(20)

    def test_address_dump(self):
        # Check that we only get address that belong to a department or union
        # And no other addresses
        departments_address = [dep.address.id for dep in Department.objects.all()]
        unions_address = [dep.address.id for dep in Union.objects.all()]

        dumped_ids = [dump["pk"] for dump in get_dump()["address"]]

        self.assertEqual(set(dumped_ids), set(departments_address + unions_address))

from django.test import TestCase
import json
from .factories import DepartmentFactory, AddressFactory, UnionFactory
from members.management.commands.dump_public_data import get_dump
from members.models import Department, Union, Address

class TestDumpData(TestCase):
    def test_address_dump(self):
        # Check that we only get address that belong to a department or union
        # And no other addresses
        DepartmentFactory.create_batch(20)
        UnionFactory.create_batch(20)
        AddressFactory.create_batch(20)

        departments_address = [
            dep.address.id for dep in Department.objects.all()
        ]
        unions_address = [dep.address.id for dep in Union.objects.all()]

        dumped_ids = [dump["pk"] for dump in save_dump()["address"]]

        self.assertEqual(set(dumped_ids), set(departments_address + unions_address))

from django.test import TestCase
from members.models import (
    DailyStatisticsGeneral,
    DailyStatisticsRegion,
    DailyStatisticsUnion,
)
from members.models.statistics import DepartmentStatistics
from graphene.test import Client
from members.schema import schema
from .factories import UnionFactory, DepartmentFactory, VolunteerFactory
from random import randint


class TestQueryDailyStatisticsGeneral(TestCase):
    def setUp(self):
        self.union = UnionFactory()
        self.union.save()
        self.department = DepartmentFactory()
        self.nr_voluenteers = randint(1, 100)
        VolunteerFactory.create_batch(self.nr_voluenteers, department=self.department)
        DepartmentStatistics(department=self.department).save()
        DailyStatisticsGeneral(persons=42, children_male=1337).save()
        DailyStatisticsRegion(region="DK01", departments=42, volunteers=314).save()
        DailyStatisticsUnion(union=self.union, departments=42, payments=1337).save()

    def test_general_stats(self):
        client = Client(schema)
        executed = client.execute(
            """ { generalDailyStatistics { persons childrenMale } }"""
        )
        data = executed["data"]["generalDailyStatistics"]
        self.assertEqual(len(data), 1, "Should only be one record")
        assert dict(data[0]) == {"persons": 42, "childrenMale": 1337}

    def test_region_stats(self):
        client = Client(schema)
        executed = client.execute(
            """ { regionDailyStatistics {region departments volunteers} } """
        )
        data = executed["data"]["regionDailyStatistics"]
        self.assertEqual(len(data), 1, "Should only be one record")
        assert dict(data[0]) == {"region": "DK01", "departments": 42, "volunteers": 314}

    def test_union_stats(self):
        client = Client(schema)
        executed = client.execute(
            """ { unionDailyStatistics {union {name} departments payments} } """
        )
        data = executed["data"]["unionDailyStatistics"]
        self.assertEqual(len(data), 1, "Should only be one record")
        data = data[0]
        self.assertEqual(data["union"]["name"], self.union.name)
        self.assertEqual(data["departments"], 42)
        self.assertEqual(data["payments"], 1337)

    def test_department_stats(self):
        client = Client(schema)
        executed = client.execute(
            """ { departmentStatistics {department {name} volunteers } } """
        )
        data = executed["data"]["departmentStatistics"]
        self.assertEqual(len(data), 1, "Should only be one record")
        data = data[0]
        self.assertEqual(data["department"]["name"], self.department.name)
        self.assertEqual(data["volunteers"], self.nr_voluenteers)

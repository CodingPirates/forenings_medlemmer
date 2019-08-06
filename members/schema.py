import graphene
from graphene_django.types import DjangoObjectType


from members.models import (
    Department,
    Union,
    DailyStatisticsGeneral,
    DailyStatisticsRegion,
    DailyStatisticsUnion,
)


class StatisticsGeneral(DjangoObjectType):
    class Meta:
        model = DailyStatisticsGeneral


class StatisticsRegion(DjangoObjectType):
    class Meta:
        model = DailyStatisticsRegion


class StatisticsUnion(DjangoObjectType):
    class Meta:
        model = DailyStatisticsUnion


class UnionType(DjangoObjectType):
    class Meta:
        model = Union
        exclude_fields = ("region", "bank_main_org", "bank_account")


class DepartmentType(DjangoObjectType):
    class Meta:
        model = Department
        # only_fields = ("name", "description")


class Query(graphene.ObjectType):
    unions = graphene.List(UnionType)
    departments = graphene.List(DepartmentType)
    general_daily_statistics = graphene.List(StatisticsGeneral)
    union_daily_statistics = graphene.List(StatisticsUnion)
    region_daily_statistics = graphene.List(StatisticsRegion)

    def resolve_general_daily_statistics(self, info, **kwargs):
        return DailyStatisticsGeneral.objects.all()

    def resolve_union_daily_statistics(self, info, **kwargs):
        return DailyStatisticsUnion.objects.all()

    def resolve_region_daily_statistics(self, info, **kwargs):
        return DailyStatisticsRegion.objects.all()

    def resolve_unions(self, info, **kwargs):
        return Union.objects.all()

    def resolve_departments(self, info, **kwargs):
        return Department.objects.all()


schema = graphene.Schema(query=Query)

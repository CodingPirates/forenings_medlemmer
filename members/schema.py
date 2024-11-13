import graphene
from graphene_django.types import DjangoObjectType


from members.models import (
    Department,
    Address,
    Union,
    DailyStatisticsGeneral,
    DailyStatisticsRegion,
    DailyStatisticsUnion,
)
from members.models.statistics import DepartmentStatistics as DepStatModel


class StatisticsGeneral(DjangoObjectType):
    class Meta:
        model = DailyStatisticsGeneral


class DepartmentStatistics(DjangoObjectType):
    class Meta:
        model = DepStatModel


class StatisticsRegion(DjangoObjectType):
    class Meta:
        model = DailyStatisticsRegion


class StatisticsUnion(DjangoObjectType):
    class Meta:
        model = DailyStatisticsUnion


class UnionType(DjangoObjectType):
    class Meta:
        model = Union
        exclude = ("bank_main_org", "bank_account", "gl_account")


class DepartmentType(DjangoObjectType):
    class Meta:
        model = Department


class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        exclude = ("region",)


class Query(graphene.ObjectType):
    unions = graphene.List(UnionType)
    departments = graphene.List(DepartmentType)
    general_daily_statistics = graphene.List(StatisticsGeneral)
    union_daily_statistics = graphene.List(StatisticsUnion)
    region_daily_statistics = graphene.List(StatisticsRegion)
    department_statistics = graphene.List(DepartmentStatistics)

    def resolve_department_statistics(self, info, **kwargs):
        return DepStatModel.objects.all()

    def resolve_general_daily_statistics(self, info, **kwargs):
        return DailyStatisticsGeneral.objects.all()

    def resolve_union_daily_statistics(self, info, **kwargs):
        return DailyStatisticsUnion.objects.all()

    def resolve_region_daily_statistics(self, info, **kwargs):
        return DailyStatisticsRegion.objects.all()

    def resolve_unions(self, info, **kwargs):
        return Union.objects.all()

    def resolve_departments(self, info, **kwargs):
        return filter(
            lambda dep: dep.address.region != "", Department.get_open_departments()
        )


schema = graphene.Schema(query=Query)

import graphene
import graphql_jwt
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from members.utils.user import user_to_person

from .person_mutations import CreateAdultMutation

from members.models import (
    Department,
    Union,
    DailyStatisticsGeneral,
    DailyStatisticsRegion,
    DailyStatisticsUnion,
    Person,
)
from members.models.statistics import DepartmentStatistics as DepStatModel


class StatisticsGeneral(DjangoObjectType):
    class Meta:
        model = DailyStatisticsGeneral


class PersonType(DjangoObjectType):
    class Meta:
        model = Person


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
        exclude_fields = ("region", "bank_main_org", "bank_account")


class DepartmentType(DjangoObjectType):
    class Meta:
        model = Department


class Mutation(graphene.ObjectType):
    create_adult = CreateAdultMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Query(graphene.ObjectType):
    unions = graphene.List(UnionType)
    departments = graphene.List(DepartmentType)
    general_daily_statistics = graphene.List(StatisticsGeneral)
    union_daily_statistics = graphene.List(StatisticsUnion)
    region_daily_statistics = graphene.List(StatisticsRegion)
    department_statistics = graphene.List(DepartmentStatistics)
    me = graphene.Field(PersonType)

    @login_required
    def resolve_me(self, info, **kwargs):
        return user_to_person(info.context.user)

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
        return Department.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)

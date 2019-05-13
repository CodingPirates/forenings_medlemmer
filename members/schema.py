import graphene
from graphene_django.types import DjangoObjectType


from members.models import Department, Union


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

    def resolve_unions(self, info, **kwargs):
        return Union.objects.all()

    def resolve_departments(self, info, **kwargs):
        return Department.objects.all()


schema = graphene.Schema(query=Query)

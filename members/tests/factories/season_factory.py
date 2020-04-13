import factory
from members.tests.factories.factory_helpers import TIMEZONE


from members.tests.factories.department_factory import DepartmentFactory
from django.utils import timezone
from factory import Faker, DjangoModelFactory, SubFactory, LazyAttribute


from random import randint
from members.models import Season
from datetime import time, timedelta
from members.tests.factories.person_factory import PersonFactory


class SeasonFactory(DjangoModelFactory):
    class Meta:
        model = Season
        exclude = "active"

    # Helper fields
    active = Faker("boolean")

    name = "Sæson"
    department = SubFactory(DepartmentFactory)
    start_date = LazyAttribute(
        lambda season: timezone.now() + timedelta(days=7 * randint(1, 2))
        if season.active
        else Faker("date_time", tzinfo=TIMEZONE).generate({})
    )
    end_date = LazyAttribute(
        lambda season: season.start_date + timedelta(days=30 * randint(2, 4))
    )
    week_day = LazyAttribute(lambda season: randint(1, 7))
    start_time = factory.fuzzy.FuzzyChoice([time(16, 0), time(17, 0)])
    end_time = LazyAttribute(
        lambda season: time(season.start_time.hour + randint(1, 4))
    )
    signup_closing = LazyAttribute(
        lambda season: season.start_date + timedelta(days=7 * randint(2, 6))
    )
    responsible = SubFactory(PersonFactory)  # create captain factory
    description = Faker("text")
    instructions = Faker("text")
    open_invite = LazyAttribute(
        lambda season: True if season.active else randint(0, 10) % 2 == 0
    )
    price_in_dkk = Faker("random_number", digits=4)
    # TODO switch from LazyAttribute
    max_participants = LazyAttribute(lambda season: randint(20, 50))
    max_age = LazyAttribute(lambda season: randint(6, 10))
    min_age = LazyAttribute(lambda season: randint(12, 18))

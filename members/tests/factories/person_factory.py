import factory
from factory import Faker, SubFactory, SelfAttribute
from factory.django import DjangoModelFactory
from members.tests.factories.factory_helpers import TIMEZONE, LOCALE
from members.tests.factories.municipality_factory import MunicipalityFactory
from members.tests.factories.providers import DanishProvider
from factory.fuzzy import FuzzyChoice
from members.models import Person
from members.tests.factories.family_factory import FamilyFactory
from members.tests.factories.user_factory import UserFactory

Faker.add_provider(DanishProvider, locale=LOCALE)
Faker._DEFAULT_LOCALE = "dk_DK"


def _next_person_email_index():
    """The next free index in the ``personN@example.com`` e-mails.

    The database is the source of truth for the e-mails, the same way
    Postgres is the source of truth for id sequences. This is what makes
    the sequence survive a new process such as ``manage.py shell``
    (issue #1128).
    """
    emails = Person.objects.filter(
        email__startswith="person", email__endswith="@example.com"
    ).values_list("email", flat=True)
    indices = []
    for email in emails:
        index = email[len("person") : -len("@example.com")]
        if index.isdigit():
            indices.append(int(index))
    return max(indices, default=-1) + 1


class ResyncSequence(factory.Sequence):
    """A ``factory.Sequence`` that re-syncs from the database.

    The counter of a plain ``factory.Sequence`` lives in memory, so a new
    process (e.g. a new ``manage.py shell``) starts over at 0 and runs
    into the unique constraint on the e-mail. Re-syncing from the highest
    existing ``personN@example.com`` e-mail is the equivalent of the
    ``setval`` call that re-syncs Postgres id sequences after an import.
    """

    def __init__(self, function):
        super().__init__(function)
        self._counter = None

    def evaluate(self, instance, step, extra):
        if self._counter is None:
            self._counter = _next_person_email_index()
        index = self._counter
        self._counter += 1
        return self.function(index)


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    membertype = "PA"
    name = Faker("name")
    placename = Faker("city_suffix")
    zipcode = Faker("zipcode")
    city = Faker("city")
    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    dawa_id = Faker("uuid4")
    municipality = SubFactory(MunicipalityFactory)
    longitude = Faker("longitude")
    latitude = Faker("latitude")
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    email = ResyncSequence(
        lambda n: "person{0}@example.com".format(n)
    )  # Faker("email")
    phone = Faker("phone_number")
    gender = FuzzyChoice([code for (code, name) in Person.MEMBER_GENDER_CHOICES])
    birthday = Faker("date_of_birth", minimum_age=0, maximum_age=100)
    # has_certificate = Faker("date")
    family = SubFactory(FamilyFactory, email=email)
    notes = Faker("text")
    # added_at = Faker("date_time", tzinfo=TIMEZONE)
    # deleted_dtm = Faker("date_time", tzinfo=TIMEZONE)
    user = SubFactory(
        UserFactory, username=SelfAttribute("..email"), email=SelfAttribute("..email")
    )
    address_invalid = Faker("boolean")

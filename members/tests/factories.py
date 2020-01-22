# TODO: Factories for AdminUserInformation, equipment, equipment loan, emails and statistics
# TODO: tests for departments, members, volunteers, activities, equipment, equipmentloan, statistics

import pytz
from datetime import timedelta
import random
from django.utils import timezone
from django.contrib.auth import get_user_model

import factory
from factory import Faker, DjangoModelFactory, SubFactory, LazyAttribute, SelfAttribute
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from faker.providers import BaseProvider


from members.models import (
    Activity,
    ActivityInvite,
    ActivityParticipant,
    Address,
    AdminUserInformation,
    Department,
    EmailItem,
    EmailTemplate,
    Equipment,
    EquipmentLoan,
    Family,
    Member,
    Notification,
    Payment,
    Person,
    Union,
    Volunteer,
    WaitingList,
    ZipcodeRegion,
)


class CodingPiratesProvider(BaseProvider):
    activity_types = [
        "Hackathon",
        "Gamejam",
        "Børne IT-konference",
        "Summercamp",
        "Forårssæson",
        "Efterårssæson",
    ]

    def activity_type(self):
        """ Formatter for generating random activity types
        """
        return random.choice(self.activity_types)

    def activity(self):
        """ Formatter for generating random Coding Pirates activities
        """
        pattern = "{{activity_type}} {{year}}"
        return self.generator.parse(pattern)

    payment_types = ["CA", "BA", "CC", "RE", "OT"]

    def payment_type(self):
        return random.choice(self.payment_types)


class DanishProvider(BaseProvider):
    """
    Custom faker provider for Danish addresses.
    """

    floor_formats = [
        "",
        "Stuen",
        "1. sal",
        "1",
        "1.",
        "2.",
        "0",
        "0.",
        "4.",
        "kl",
        "st",
        "kælder",
        "k2",
    ]

    door_formats = ["", "410", "th", "tv", "mf", "v28"]  # , "værelse 17"]

    city_suffixes = ["rød", "havn", "borg", "by", "bjerg", "ssund", "sværk", "ning"]
    street_suffixes = ["Vej", "Gade", "Vangen", "Stræde", "Plads"]

    def floor(self):
        """ Formatter for generating floor names in danish
        """
        return random.choice(self.floor_formats)

    def door(self):
        """ Formatter for generating door names in danish
        """
        return random.choice(self.door_formats)

    def zipcode(self):
        """ Formatter for generating door names in danish
        """
        return str(random.randint(1000, 9999))

    def city_suffix(self):
        """
        :example 'rød'
        """
        return self.random_element(self.city_suffixes)

    def street_suffix(self):
        """
        :example 'vej'
        """
        return self.random_element(self.street_suffixes)

    def city(self):
        """
        :example 'Frederiksværk'
        """
        pattern = "{{first_name}}{{city_suffix}}"
        return self.generator.parse(pattern)

    def municipality(self):
        """ Formatter for generating danish municipality names
        """
        return self.generator.parse("{{city}} kommune")

    def street_name(self):
        """ Formatter for generating danish street names
        """
        return self.generator.parse("{{name}}s {{street_suffix}}")


Faker.add_provider(CodingPiratesProvider, locale="dk_DK")
Faker.add_provider(DanishProvider, locale="dk_DK")


LOCALE = "dk_DK"
TIMEZONE = pytz.timezone("Europe/Copenhagen")
# Setting default locale (this is not documented or intended by factory_boy)
Faker._DEFAULT_LOCALE = LOCALE


def datetime_before(datetime):
    return datetime - timedelta(days=random.randint(1, 4 * 365))


def datetime_after(datetime):
    return datetime + timedelta(days=random.randint(1, 4 * 365))


class ZipcodeRegionFactory(DjangoModelFactory):
    class Meta:
        model = ZipcodeRegion

    region = FuzzyChoice(ZipcodeRegion.REGION_CHOICES)
    zipcode = Faker("zipcode")
    city = Faker("city")
    municipalname = Faker("municipality")
    municipalcode = Faker("numerify", text="###")
    longitude = Faker("longitude")
    latitude = Faker("latitude")


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    city = Faker("city")
    zipcode = Faker("zipcode")
    municipality = Faker("municipality")
    longitude = Faker("longitude")
    latitude = Faker("latitude")


class FamilyFactory(DjangoModelFactory):
    class Meta:
        model = Family

    unique = Faker("uuid4")
    # email = Faker("email")
    email = factory.Sequence(
        lambda n: "family{0}@example.com".format(n)
    )  # Faker("email")
    # dont_send_mails = Faker("boolean")
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    confirmed_dtm = Faker("date_time", tzinfo=TIMEZONE)
    last_visit_dtm = Faker("date_time", tzinfo=TIMEZONE)
    deleted_dtm = Faker("date_time", tzinfo=TIMEZONE)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()


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
    municipality = Faker("municipality")
    longitude = Faker("longitude")
    latitude = Faker("latitude")
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    email = factory.Sequence(
        lambda n: "person{0}@example.com".format(n)
    )  # Faker("email")
    phone = Faker("phone_number")
    gender = FuzzyChoice([code for (code, name) in Person.MEMBER_GENDER_CHOICES])
    birthday = Faker("date")
    # has_certificate = Faker("date")
    family = SubFactory(FamilyFactory, email=email)
    notes = Faker("text")
    # added = Faker("date_time", tzinfo=TIMEZONE)
    # deleted_dtm = Faker("date_time", tzinfo=TIMEZONE)
    user = SubFactory(
        UserFactory, username=SelfAttribute("..email"), email=SelfAttribute("..email")
    )
    address_invalid = Faker("boolean")


class UnionFactory(DjangoModelFactory):
    class Meta:
        model = Union

    name = factory.LazyAttribute(lambda u: "Coding Pirates {}".format(u.address.city))
    chairman = Faker("name")
    chairman = Faker("email")
    second_chair = Faker("name")
    second_chair_email = Faker("email")
    cashier = Faker("name")
    cashier_email = Faker("email")
    secretary = Faker("name")
    secratary_email = Faker("email")
    union_email = Faker("email")
    statues = Faker("url")
    founded = Faker("date_time", tzinfo=TIMEZONE)
    region = FuzzyChoice([r[0] for r in Union.regions])
    address = SubFactory(AddressFactory)
    boardMembers = Faker("text")
    bank_main_org = Faker("boolean")
    bank_account = Faker("numerify", text="####-##########")


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    name = Faker("city")
    description = Faker("text")
    open_hours = Faker("numerify", text="kl. ##:##-##:##")
    responsible_name = Faker("name")
    responsible_contact = Faker("email")
    created = Faker("date_time", tzinfo=TIMEZONE)
    updated_dtm = LazyAttribute(lambda d: datetime_after(d.created))
    closed_dtm = LazyAttribute(lambda d: datetime_after(d.created))
    isVisible = Faker("boolean")
    isOpening = Faker("boolean")
    website = Faker("url")
    union = SubFactory(UnionFactory)
    address = SubFactory(AddressFactory)
    onMap = Faker("boolean")


class MemberFactory(DjangoModelFactory):
    class Meta:
        model = Member

    department = SubFactory(DepartmentFactory)
    person = SubFactory(PersonFactory)
    # is_active = Faker("boolean")
    member_since = Faker("date_time", tzinfo=TIMEZONE)
    # member_until = LazyAttribute(lambda m: None if m.is_active else datetime_after(m.member_since))


class VolunteerFactory(DjangoModelFactory):
    class Meta:
        model = Volunteer

    person = SubFactory(PersonFactory)
    department = SubFactory(DepartmentFactory)

    added = Faker("date_time", tzinfo=TIMEZONE)
    confirmed = LazyAttribute(lambda d: datetime_after(d.added))
    removed = LazyAttribute(lambda d: datetime_after(d.added))


class WaitingListFactory(DjangoModelFactory):
    class Meta:
        model = WaitingList

    person = SubFactory(PersonFactory)
    department = SubFactory(DepartmentFactory)
    on_waiting_list_since = Faker("date_time", tzinfo=TIMEZONE)
    added_dtm = Faker("date_time", tzinfo=TIMEZONE)


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity
        exclude = ("active", "now")

    # Helper fields
    active = Faker("boolean")
    now = timezone.now()

    union = SubFactory(UnionFactory)
    department = SubFactory(DepartmentFactory, union=factory.SelfAttribute("..union"))
    name = Faker("activity")
    open_hours = Faker("numerify", text="kl. ##:00-##:00")
    responsible_name = Faker("name")
    responsible_contact = Faker("email")
    placename = Faker("city_suffix")
    zipcode = Faker("zipcode")
    city = Faker("city")
    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    dawa_id = Faker("uuid4")
    description = Faker("text")
    instructions = Faker("text")
    signup_closing = Faker("date_time", tzinfo=TIMEZONE)
    start_date = LazyAttribute(
        lambda d: datetime_before(d.now)
        if d.active
        else Faker("date_time", tzinfo=TIMEZONE).generate({})
    )
    end_date = LazyAttribute(
        lambda d: datetime_after(d.now) if d.active else datetime_before(d.now)
    )
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    open_invite = Faker("boolean")
    price_in_dkk = Faker("random_number", digits=4)
    max_participants = Faker("random_number")
    min_age = Faker("random_number")
    max_age = LazyAttribute(lambda a: a.min_age + Faker("random_number").generate({}))
    member_justified = Faker("boolean")


class ActivityParticipantFactory(DjangoModelFactory):
    class Meta:
        model = ActivityParticipant

    added_dtm = Faker("date_time", tzinfo=TIMEZONE)
    activity = SubFactory(ActivityFactory)
    member = SubFactory(MemberFactory)
    note = Faker("text")
    photo_permission = "OK" if random.randint(0, 1) == 1 else "NO"
    contact_visible = Faker("boolean")


class ActivityInviteFactory(DjangoModelFactory):
    class Meta:
        model = ActivityInvite

    activity = SubFactory(ActivityFactory)
    person = SubFactory(PersonFactory)
    invite_dtm = Faker("date_time", tzinfo=TIMEZONE)
    expire_dtm = LazyAttribute(lambda d: datetime_after(d.invite_dtm))
    rejected_dtm = LazyAttribute(lambda d: datetime_after(d.invite_dtm))


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    payment_type = Faker("payment_type")
    activity = SubFactory(ActivityFactory)
    activityparticipant = SubFactory(ActivityParticipantFactory)
    person = SubFactory(PersonFactory)
    family = SubFactory(FamilyFactory)
    body_text = Faker("text")
    amount_ore = FuzzyInteger(10000, 70000)
    confirmed_dtm = Faker("date_time", tzinfo=TIMEZONE)
    cancelled_dtm = Faker("date_time", tzinfo=TIMEZONE)
    refunded_dtm = Faker("date_time", tzinfo=TIMEZONE)
    rejected_dtm = Faker("date_time", tzinfo=TIMEZONE)
    rejected_message = Faker("text")


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    city = Faker("city")
    zipcode = Faker("zipcode")
    municipality = Faker("municipality")
    longitude = Faker("longitude")
    latitude = Faker("latitude")


class AdminUserInformationFactory(DjangoModelFactory):
    class Meta:
        model = AdminUserInformation

    # TODO


class EmailItemFactory(DjangoModelFactory):
    class Meta:
        model = EmailItem

    # TODO


class EmailTemplateFactory(DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    # TODO


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    # TODO


class EquipmentFactory(DjangoModelFactory):
    class Meta:
        model = Equipment


class EquipmentLoanFactory(DjangoModelFactory):
    class Meta:
        model = EquipmentLoan

    # TODO

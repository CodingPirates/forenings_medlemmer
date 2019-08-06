# TODO: Factories for AdminUserInformation, equipment, equipment loan, emails and statistics
# TODO: tests for departments, members, volunteers, activities, equipment, equipmentloan, statistics

import pytz
from datetime import date, timedelta
import random

from django.contrib.auth import get_user_model

import factory
from factory import Faker, DjangoModelFactory, SubFactory, LazyAttribute, SelfAttribute
from factory.fuzzy import FuzzyChoice
from faker.providers import BaseProvider

from members.models.family import Family
from members.models.zipcoderegion import ZipcodeRegion
from members.models.person import Person
from members.models.volunteer import Volunteer
from members.models.union import Union
from members.models.department import Department, AdminUserInformation
from members.models.member import Member
from members.models.waitinglist import WaitingList
from members.models.activity import Activity
from members.models.activityparticipant import ActivityParticipant
from members.models.activityinvite import ActivityInvite
from members.models.payment import Payment
from members.models.emailitem import EmailItem
from members.models.emailtemplate import EmailTemplate
from members.models.notification import Notification
from members.models.equipment import Equipment
from members.models.equipmentloan import EquipmentLoan


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


def datetime_after(dt):
    """
    For use with lazy attribute to generate DateTime's after the given
    datetime.
    """
    END_OF_TIME = date.today() + timedelta(days=60 * 365)
    return Faker(
        "date_time_between", tzinfo=TIMEZONE, start_date=dt, end_date=END_OF_TIME
    ).generate({})


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

    # membertype = FuzzyChoice(Person.MEMBER_TYPE_CHOICES)
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
    gender = FuzzyChoice(Person.MEMBER_GENDER_CHOICES)
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

    city = Faker("city")
    placename = Faker("city")
    name = factory.LazyAttribute(lambda u: "Coding Pirates {}".format(u.city))
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
    zipcode = Faker("zipcode")
    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    boardMembers = Faker("text")
    # bank_main_org = Faker("boolean")
    bank_account = Faker("numerify", text="####-##########")


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    name = Faker("city")
    description = Faker("text")
    open_hours = Faker("numerify", text="kl. ##:##-##:##")
    responsible_name = Faker("name")
    responsible_contact = Faker("email")
    zipcode = Faker("zipcode")
    city = Faker("city")
    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    dawa_id = Faker("uuid4")
    has_waiting_list = Faker("boolean")
    created = Faker("date_time", tzinfo=TIMEZONE)
    updated_dtm = LazyAttribute(lambda d: datetime_after(d.created))
    closed_dtm = LazyAttribute(lambda d: datetime_after(d.created))
    isVisible = Faker("boolean")
    isOpening = Faker("boolean")
    website = Faker("url")
    union = SubFactory(UnionFactory)
    longitude = Faker("longitude")
    latitude = Faker("latitude")
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

    department = SubFactory(DepartmentFactory)
    union = SubFactory(UnionFactory)
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
    start_date = LazyAttribute(lambda d: datetime_after(d.signup_closing))
    end_date = LazyAttribute(lambda d: datetime_after(d.start_date))
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    open_invite = Faker("boolean")
    price_in_dkk = Faker("random_number")
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
    photo_permission = FuzzyChoice(ActivityParticipant.PHOTO_PERMISSION_CHOICES)
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

    added = Faker("date_time", tzinfo=TIMEZONE)
    payment_type = FuzzyChoice(Payment.PAYMENT_METHODS)
    activity = SubFactory(ActivityFactory)
    activityparticipant = SubFactory(ActivityParticipantFactory)
    person = SubFactory(PersonFactory)
    family = SubFactory(FamilyFactory)
    body_text = Faker("text")
    amount_ore = Faker("random_number")
    confirmed_dtm = Faker("date_time", tzinfo=TIMEZONE)
    cancelled_dtm = Faker("date_time", tzinfo=TIMEZONE)
    refunded_dtm = Faker("date_time", tzinfo=TIMEZONE)
    rejected_dtm = Faker("date_time", tzinfo=TIMEZONE)
    rejected_message = Faker("text")


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

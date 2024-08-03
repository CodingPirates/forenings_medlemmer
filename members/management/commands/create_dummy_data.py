from django.core.management.base import BaseCommand
from factory.fuzzy import FuzzyChoice

from members.models import Address
from members.tests.factories import (
    PersonFactory,
    UnionFactory,
    DepartmentFactory,
    WaitingListFactory,
    FamilyFactory,
    ActivityFactory,
    ActivityParticipantFactory,
    AddressFactory,
)
from factory import Faker
from django.utils import timezone
from collections import namedtuple

# We're creating a union for each region.
# A named tuple with a name for the Union, and a name for the region to use in its address.
Union_to_create = namedtuple("Union_to_create", "union_name region_name")
UNIONS_TO_CREATE = [
    Union_to_create(union_name="Syddanmark", region_name="Region Syddanmark"),
    Union_to_create(union_name="Hovedstaden", region_name="Region Hovedstaden"),
    Union_to_create(union_name="Nordjylland", region_name="Region Nordjylland"),
    Union_to_create(union_name="Midtjylland", region_name="Region Midtjylland"),
    Union_to_create(union_name="Sjælland", region_name="Region Sjælland"),
]


class Command(BaseCommand):
    help = (
        "Generates dummy data and adds it to the system. It will generate: "
        f"{len(UNIONS_TO_CREATE)} unions in total. 2 departments per union. 2 activities per department, "
        "with 2 children in each. Additionally each department will have 1 or 2 children on the "
        "waiting list, and all children will have one parent and family. "
        f"Unions that'll be created: {str.join(', ', (x.union_name for x in UNIONS_TO_CREATE))}"
    )

    def handle(self, *args, **options):
        # Setting up unions
        for union_to_create in UNIONS_TO_CREATE:
            print(f"**Creating union: {union_to_create.union_name}**")
            union = UnionFactory(
                name=union_to_create.union_name,
                address=AddressFactory(region=union_to_create.region_name),
            )
            _setup_waitlist(
                _create_department(union=union), _create_department(union=union)
            )
        # Notify when command has finished
        print("**Finished**")


# Creates 2 children and makes them waitlisted (One child on waiting list for
# the first department only, and one child on waiting list for both departments)
def _setup_waitlist(department1, department2):
    print("Creating waiting list.")
    # Child on waiting list for the first department only:
    WaitingListFactory(person=_create_child(), department=department1)
    # Child on waiting list for both departments:
    child_on_both_waiting_lists = _create_child()
    WaitingListFactory(person=child_on_both_waiting_lists, department=department1)
    WaitingListFactory(person=child_on_both_waiting_lists, department=department2)


# Creates a department following the requirements: 2 activities per department with 2 children per activity.
def _create_department(union):
    department = DepartmentFactory(
        union=union,
        address=AddressFactory(region=union.address.region),
        closed_dtm=None,
    )
    _create_activity(department)
    _create_activity(department)
    print("Created department")
    return department


# Creates an activity with 2 children
def _create_activity(department):
    start_date = timezone.now()
    end_date = start_date + timezone.timedelta(
        days=Faker("random_int", min=10, max=100).generate({})
    )
    activity = ActivityFactory(
        name=Faker("activity", year=start_date.year),
        department=department,
        union=department.union,
        start_date=start_date,
        end_date=end_date,
        max_participants=Faker("random_int", min=10, max=100),
        price_in_dkk=Faker("random_int", min=500, max=1000),
        address=AddressFactory(region=department.address.region),
    )
    # Creates 2 children and assigns them to the activity
    ActivityParticipantFactory(person=_create_child(), activity=activity)
    ActivityParticipantFactory(person=_create_child(), activity=activity)
    print("Created activity")
    return activity


# Creates a child, a parent, and a family.
# Function returns the child
def _create_child():
    family = FamilyFactory()
    parent = PersonFactory(membertype="PA", family=family, email=family.email)
    child = PersonFactory(
        membertype="CH",
        family=family,
        placename=parent.placename,
        zipcode=parent.zipcode,
        city=parent.city,
        streetname=parent.streetname,
        housenumber=parent.housenumber,
        floor=parent.floor,
        door=parent.door,
        dawa_id=parent.dawa_id,
        municipality=parent.municipality,
        longitude=parent.longitude,
        latitude=parent.latitude,
    )
    print("Created child, parent and family")
    return child

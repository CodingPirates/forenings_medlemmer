import datetime

from django.db.models.functions import Coalesce
from django.db.models import Sum


from members.models import (
    Activity,
    ActivityParticipant,
    DailyStatisticsGeneral,
    DailyStatisticsRegion,
    DailyStatisticsUnion,
    Department,
    Family,
    Payment,
    Person,
    Union,
    ZipcodeRegion,
)


def old_stat_code(timestamp):
    # generate general statistics
    dailyStatisticsGeneral = DailyStatisticsGeneral()

    dailyStatisticsGeneral.timestamp = timestamp
    dailyStatisticsGeneral.persons = Person.objects.count()
    dailyStatisticsGeneral.children_male = Person.objects.filter(
        membertype=Person.CHILD, gender=Person.MALE
    ).count()
    dailyStatisticsGeneral.children_female = Person.objects.filter(
        membertype=Person.CHILD, gender=Person.FEMALE
    ).count()
    dailyStatisticsGeneral.children = (
        dailyStatisticsGeneral.children_male + dailyStatisticsGeneral.children_female
    )
    dailyStatisticsGeneral.volunteers_male = Person.objects.filter(
        gender=Person.MALE, volunteer__isnull=False
    ).count()
    dailyStatisticsGeneral.volunteers_female = Person.objects.filter(
        gender=Person.FEMALE, volunteer__isnull=False
    ).count()
    dailyStatisticsGeneral.volunteers = (
        dailyStatisticsGeneral.volunteers_male
        + dailyStatisticsGeneral.volunteers_female
    )
    dailyStatisticsGeneral.departments = Department.objects.filter(
        closed_dtm=None
    ).count()
    dailyStatisticsGeneral.unions = Union.objects.count()
    dailyStatisticsGeneral.waitinglist_male = (
        Person.objects.filter(waitinglist__isnull=False, gender=Person.MALE)
        .distinct()
        .count()
    )
    dailyStatisticsGeneral.waitinglist_female = (
        Person.objects.filter(waitinglist__isnull=False, gender=Person.FEMALE)
        .distinct()
        .count()
    )
    dailyStatisticsGeneral.waitinglist = (
        dailyStatisticsGeneral.waitinglist_male
        + dailyStatisticsGeneral.waitinglist_female
    )
    dailyStatisticsGeneral.family_visits = Family.objects.filter(
        last_visit_dtm__gt=(timestamp - datetime.timedelta(days=1))
    ).count()
    dailyStatisticsGeneral.dead_profiles = Family.objects.filter(
        last_visit_dtm__lt=(timestamp - datetime.timedelta(days=365))
    ).count()
    dailyStatisticsGeneral.current_activity_participants = (
        Person.objects.filter(
            activityparticipant__activity__end_date__gte=timestamp,
            activityparticipant__activity__start_date__lte=timestamp,
        )
        .distinct()
        .count()
    )
    dailyStatisticsGeneral.activity_participants_male = (
        Person.objects.filter(
            activityparticipant__activity__isnull=False, gender=Person.MALE
        )
        .distinct()
        .count()
    )
    dailyStatisticsGeneral.activity_participants_female = (
        Person.objects.filter(
            activityparticipant__activity__isnull=False,
            gender=Person.FEMALE,
        )
        .distinct()
        .count()
    )
    dailyStatisticsGeneral.activity_participants = (
        dailyStatisticsGeneral.activity_participants_male
        + dailyStatisticsGeneral.activity_participants_female
    )
    dailyStatisticsGeneral.payments = Payment.objects.filter(
        refunded_at=None, confirmed_at__isnull=False
    ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]
    dailyStatisticsGeneral.payments_transactions = Payment.objects.filter(
        refunded_at=None, confirmed_at__isnull=False
    ).count()
    dailyStatisticsGeneral.save()

    # generate daily union statistics
    unions = Union.objects.all()
    for union in unions:
        dailyStatisticsUnion = DailyStatisticsUnion()

        dailyStatisticsUnion.timestamp = timestamp
        dailyStatisticsUnion.union = union
        dailyStatisticsUnion.departments = Department.objects.filter(
            union=union
        ).count()
        dailyStatisticsUnion.active_activities = Activity.objects.filter(
            department__union=union,
            start_date__lte=timestamp,
            end_date__gte=timestamp,
        ).count()
        dailyStatisticsUnion.activities = Activity.objects.filter(
            department__union=union
        ).count()
        dailyStatisticsUnion.current_activity_participants = (
            Person.objects.filter(
                activityparticipant__activity__start_date__lte=timestamp,
                activityparticipant__activity__end_date__gte=timestamp,
                activityparticipant__activity__department__union=union,
            )
            .distinct()
            .count()
        )
        dailyStatisticsUnion.activity_participants = ActivityParticipant.objects.filter(
            activity__department__union=union
        ).count()
        dailyStatisticsUnion.members = 0  # TODO: to loosely defined now
        dailyStatisticsUnion.waitinglist = (
            Person.objects.filter(waitinglist__department__union=union)
            .distinct()
            .count()
        )
        dailyStatisticsUnion.payments = Payment.objects.filter(
            activity__department__union=union,
            refunded_at=None,
            confirmed_at__isnull=False,
        ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]
        dailyStatisticsUnion.volunteers_male = (
            Person.objects.filter(
                volunteer__department__union=union, gender=Person.MALE
            )
            .distinct()
            .count()
        )
        dailyStatisticsUnion.volunteers_female = (
            Person.objects.filter(
                volunteer__department__union=union, gender=Person.FEMALE
            )
            .distinct()
            .count()
        )
        dailyStatisticsUnion.volunteers = (
            dailyStatisticsUnion.volunteers_male
            + dailyStatisticsUnion.volunteers_female
        )

        dailyStatisticsUnion.save()

    # generate daily region statistics
    regions = ("DK01", "DK02", "DK03", "DK04", "DK05")
    for region in regions:
        dailyStatisticsRegion = DailyStatisticsRegion()

        zipsInRegion = ZipcodeRegion.objects.filter(region=region).values_list(
            "zipcode", flat=True
        )  # There are no easy foreing key to identify region

        dailyStatisticsRegion.timestamp = timestamp
        dailyStatisticsRegion.region = region
        # No unions - since unions may span regions
        dailyStatisticsRegion.departments = (
            Department.objects.annotate()
            .filter(address__zipcode__in=zipsInRegion)
            .count()
        )
        dailyStatisticsRegion.active_activities = Activity.objects.filter(
            department__address__zipcode__in=zipsInRegion,
            start_date__lte=timestamp,
            end_date__gte=timestamp,
        ).count()
        dailyStatisticsRegion.activities = Activity.objects.filter(
            department__address__zipcode__in=zipsInRegion
        ).count()
        dailyStatisticsRegion.current_activity_participants = (
            Person.objects.filter(
                activityparticipant__activity__start_date__lte=timestamp,
                activityparticipant__activity__end_date__gte=timestamp,
                activityparticipant__activity__department__address__zipcode__in=zipsInRegion,
            )
            .distinct()
            .count()
        )
        dailyStatisticsRegion.activity_participants = (
            ActivityParticipant.objects.filter(
                activity__department__address__zipcode__in=zipsInRegion
            ).count()
        )
        dailyStatisticsRegion.members = 0  # TODO: to loosely defined now
        dailyStatisticsRegion.waitinglist = (
            Person.objects.filter(
                waitinglist__department__address__zipcode__in=zipsInRegion
            )
            .distinct()
            .count()
        )
        dailyStatisticsRegion.payments = Payment.objects.filter(
            activity__department__address__zipcode__in=zipsInRegion,
            refunded_at=None,
            confirmed_at__isnull=False,
        ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]
        dailyStatisticsRegion.volunteers_male = (
            Person.objects.filter(
                volunteer__department__address__zipcode__in=zipsInRegion,
                gender=Person.MALE,
            )
            .distinct()
            .count()
        )
        dailyStatisticsRegion.volunteers_female = (
            Person.objects.filter(
                volunteer__department__address__zipcode__in=zipsInRegion,
                gender=Person.FEMALE,
            )
            .distinct()
            .count()
        )
        dailyStatisticsRegion.volunteers = (
            dailyStatisticsRegion.volunteers_male
            + dailyStatisticsRegion.volunteers_female
        )

        dailyStatisticsRegion.save()

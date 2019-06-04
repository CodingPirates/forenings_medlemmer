from django.conf import settings
from django_cron import CronJobBase, Schedule
from members.models.emailitem import EmailItem
from members.models.notification import Notification
from members.models.emailtemplate import EmailTemplate
from members.models.activityparticipant import ActivityParticipant
from members.models.payment import Payment
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.models.department import Department
from members.models.union import Union
from members.models.activity import Activity
from members.models.dailystatisticsgeneral import DailyStatisticsGeneral
from members.models.dailystatisticsregion import DailyStatisticsRegion
from members.models.dailystatisticsunion import DailyStatisticsUnion
import members.models.dailystatisticsdepartment
from members.models.zipcoderegion import ZipcodeRegion
from members.models.family import Family
from django.db.models import Q, F
from django.db.models import Sum
from django.db.models.functions import Coalesce
import datetime
from django.utils import timezone


# Send confirmations to Activity signups, which do not have failed payments
class SendActivitySignupConfirmationsCronJob(CronJobBase):
    RUN_EVERY_MINS = 5  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "members.send_activity_signup_confirmation_cronjob"  # a unique code

    def do(self):
        unannounced_signups = ActivityParticipant.objects.exclude(
            notification__isnull=False
        ).filter(payment__confirmed_dtm__isnull=False)

        for announcement in unannounced_signups:
            context = {
                "activity": announcement.activity,
                "person": announcement.member.person,
                "family": announcement.member.person.family,
                "union": announcement.activity.department.union,
            }
            emails = EmailTemplate.objects.get(idname="ACT_CONFIRM").makeEmail(
                [announcement.member.person, announcement.member.person.family], context
            )
            for email in emails:
                notification = Notification(
                    family=announcement.member.person.family,
                    email=email,
                    anounced_activity_participant=announcement,
                )
                notification.save()


# Send out all queued emails
class EmailSendCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "members.email_send_cronjob"  # a unique code

    def do(self):
        for curEmail in EmailItem.objects.filter(sent_dtm=None):
            curEmail.send()


class UpdateDawaData(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "members.update_dawa_data"

    def do(self):
        persons = (
            Person.objects.filter(municipality__isnull=True)
            .exclude(streetname__exact="")
            .exclude(address_invalid__exact=True)[:50]
        )

        for person in persons:
            person.update_dawa_data()


# Find families, which needs to update their information
class RequestConfirmationCronJob(CronJobBase):
    RUN_AT_TIMES = ["15:00"]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = "members.request_confirmation_cronjob"  # a unique code

    def do(self):
        # Find all Families, which has an updated_dtm older than the specified time for updates from today.
        # Exclude the families which has already received a notification after they updated last.
        # (to avoid sending again)
        outdated_dtm = timezone.now() - datetime.timedelta(
            days=settings.REQUEST_FAMILY_VALIDATION_PERIOD
        )
        unconfirmed_families = Family.objects.filter(
            Q(confirmed_dtm__lt=outdated_dtm) | Q(confirmed_dtm=None)
        ).exclude(
            Q(notification__update_info_dtm__gt=F("confirmed_dtm"))
            | Q(~Q(notification__update_info_dtm=None), confirmed_dtm=None)
        )[
            :10
        ]

        # send notification to all families asking them to update
        # their family details
        for family in unconfirmed_families:
            emails = EmailTemplate.objects.get(idname="UPDATE_DATA").makeEmail(
                family, {}
            )
            for email in emails:
                notification = Notification(
                    family=family, email=email, update_info_dtm=timezone.now()
                )
                notification.save()


# Poll payments which did not recieve callback
class PollQuickpayPaymentsCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "members.poll_quickpayPayments_cronjob"  # a unique code

    def do(self):
        outdated_dtm = timezone.now() - datetime.timedelta(
            days=14
        )  # Timeout checking payments after 14 days
        payments = Payment.objects.filter(
            rejected_dtm__isnull=True,
            confirmed_dtm__isnull=True,
            payment_type=Payment.CREDITCARD,
            added__gt=outdated_dtm,
        )

        for payment in payments:
            payment.get_quickpaytransaction().update_status()


# Daily statistics job
class GenerateStatisticsCronJob(CronJobBase):
    RUN_AT_TIMES = ["23:55"]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = "members.generate_statistics_cronjob"  # a unique code

    def do(self):
        timestamp = timezone.now()  # make sure all entries share same timestamp

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
            dailyStatisticsGeneral.children_male
            + dailyStatisticsGeneral.children_female
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
                member__activityparticipant__activity__end_date__gte=timestamp,
                member__activityparticipant__activity__start_date__lte=timestamp,
            )
            .distinct()
            .count()
        )
        dailyStatisticsGeneral.activity_participants_male = (
            Person.objects.filter(
                member__activityparticipant__activity__isnull=False, gender=Person.MALE
            )
            .distinct()
            .count()
        )
        dailyStatisticsGeneral.activity_participants_female = (
            Person.objects.filter(
                member__activityparticipant__activity__isnull=False,
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
            refunded_dtm=None, confirmed_dtm__isnull=False
        ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]
        dailyStatisticsGeneral.payments_transactions = Payment.objects.filter(
            refunded_dtm=None, confirmed_dtm__isnull=False
        ).count()
        dailyStatisticsGeneral.save()

        # generate daily department statistics
        departments = Department.objects.filter(closed_dtm=None)
        for department in departments:
            dailyStatisticsDepartment = (
                members.models.dailystatisticsdepartment.DailyStatisticsDepartment()
            )

            dailyStatisticsDepartment.timestamp = timestamp
            dailyStatisticsDepartment.department = department
            dailyStatisticsDepartment.active_activities = Activity.objects.filter(
                department=department,
                start_date__lte=timestamp,
                end_date__gte=timestamp,
            ).count()
            dailyStatisticsDepartment.activities = Activity.objects.filter(
                department=department
            ).count()
            dailyStatisticsDepartment.current_activity_participants = (
                Person.objects.filter(
                    member__activityparticipant__activity__start_date__lte=timestamp,
                    member__activityparticipant__activity__end_date__gte=timestamp,
                    member__activityparticipant__activity__department=department,
                )
                .distinct()
                .count()
            )
            dailyStatisticsDepartment.activity_participants = ActivityParticipant.objects.filter(
                activity__department=department
            ).count()
            dailyStatisticsDepartment.members = 0  # TODO: to loosely defined now
            dailyStatisticsDepartment.waitinglist = (
                Person.objects.filter(waitinglist__department=department)
                .distinct()
                .count()
            )
            firstWaitingListItem = (
                WaitingList.objects.filter(department=department)
                .order_by("on_waiting_list_since")
                .first()
            )
            if firstWaitingListItem:
                dailyStatisticsDepartment.waitingtime = (
                    timestamp - firstWaitingListItem.on_waiting_list_since
                )
            else:
                dailyStatisticsDepartment.waitingtime = datetime.timedelta(days=0)
            dailyStatisticsDepartment.payments = Payment.objects.filter(
                activity__department=department,
                refunded_dtm=None,
                confirmed_dtm__isnull=False,
            ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]
            dailyStatisticsDepartment.volunteers_male = (
                Person.objects.filter(
                    volunteer__department=department, gender=Person.MALE
                )
                .distinct()
                .count()
            )
            dailyStatisticsDepartment.volunteers_female = (
                Person.objects.filter(
                    volunteer__department=department, gender=Person.FEMALE
                )
                .distinct()
                .count()
            )
            dailyStatisticsDepartment.volunteers = (
                dailyStatisticsDepartment.volunteers_male
                + dailyStatisticsDepartment.volunteers_female
            )

            dailyStatisticsDepartment.save()

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
                    member__activityparticipant__activity__start_date__lte=timestamp,
                    member__activityparticipant__activity__end_date__gte=timestamp,
                    member__activityparticipant__activity__department__union=union,
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
                refunded_dtm=None,
                confirmed_dtm__isnull=False,
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
                Department.objects.annotate().filter(zipcode__in=zipsInRegion).count()
            )
            dailyStatisticsRegion.active_activities = Activity.objects.filter(
                department__zipcode__in=zipsInRegion,
                start_date__lte=timestamp,
                end_date__gte=timestamp,
            ).count()
            dailyStatisticsRegion.activities = Activity.objects.filter(
                department__zipcode__in=zipsInRegion
            ).count()
            dailyStatisticsRegion.current_activity_participants = (
                Person.objects.filter(
                    member__activityparticipant__activity__start_date__lte=timestamp,
                    member__activityparticipant__activity__end_date__gte=timestamp,
                    member__activityparticipant__activity__department__zipcode__in=zipsInRegion,
                )
                .distinct()
                .count()
            )
            dailyStatisticsRegion.activity_participants = ActivityParticipant.objects.filter(
                activity__department__zipcode__in=zipsInRegion
            ).count()
            dailyStatisticsRegion.members = 0  # TODO: to loosely defined now
            dailyStatisticsRegion.waitinglist = (
                Person.objects.filter(waitinglist__department__zipcode__in=zipsInRegion)
                .distinct()
                .count()
            )
            dailyStatisticsRegion.payments = Payment.objects.filter(
                activity__department__zipcode__in=zipsInRegion,
                refunded_dtm=None,
                confirmed_dtm__isnull=False,
            ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]
            dailyStatisticsRegion.volunteers_male = (
                Person.objects.filter(
                    volunteer__department__zipcode__in=zipsInRegion, gender=Person.MALE
                )
                .distinct()
                .count()
            )
            dailyStatisticsRegion.volunteers_female = (
                Person.objects.filter(
                    volunteer__department__zipcode__in=zipsInRegion,
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


# TODO:Find created families/persons, which never clicked the link (spambots etc.)

# TODO:Find families which are about to get deleted from the list and send warning

# TODO:Find Members which are active, but have expired memberships

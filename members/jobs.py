from django.conf import settings
from django_cron import CronJobBase, Schedule
from members.models import EmailItem, Family, Notification, EmailTemplate, ActivityParticipant, Payment, \
    DailyStatisticsDepartment, DailyStatisticsGeneral, Person, WaitingList, Department, Union, Activity
from django.db.models import Q, F
from django.db.models import Count, Avg
import datetime
from django.utils import timezone

# Send confirmations to Activity signups, which do not have failed payments
class SendActivitySignupConfirmationsCronJob(CronJobBase):
    RUN_EVERY_MINS = 5 # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'members.send_activity_signup_confirmation_cronjob'    # a unique code

    def do(self):
        unannounced_signups = ActivityParticipant.objects.exclude(notification__isnull=False).filter(payment__confirmed_dtm__isnull=False)

        for announcement in unannounced_signups:
            context = {
                'activity' : announcement.activity,
                'person' : announcement.member.person,
                'family' : announcement.member.person.family
            }
            emails = EmailTemplate.objects.get(idname='ACT_CONFIRM').makeEmail([announcement.member.person, announcement.member.person.family], context)
            for email in emails:
                notification = Notification(family=announcement.member.person.family, email=email, anounced_activity_participant=announcement)
                notification.save()


# Send out all queued emails
class EmailSendCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'members.email_send_cronjob'    # a unique code

    def do(self):
        for curEmail in EmailItem.objects.filter(sent_dtm=None):
            curEmail.send()

# Find families, which needs to update their information
class RequestConfirmationCronJob(CronJobBase):
    RUN_AT_TIMES = ['15:00',]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = 'members.request_confirmation_cronjob'    # a unique code


    def do(self):
        # Find all Families, which has an updated_dtm older than the specified time for updates from today.
        # Exclude the families which has already received a notification after they updated last.
        # (to avoid sending again)
        outdated_dtm = timezone.now() - datetime.timedelta(days=settings.REQUEST_FAMILY_VALIDATION_PERIOD)
        unconfirmed_families = Family.objects.filter(Q(confirmed_dtm__lt=outdated_dtm) | Q(confirmed_dtm=None)).exclude(Q(notification__update_info_dtm__gt=F('confirmed_dtm')) | Q(~Q(notification__update_info_dtm=None), confirmed_dtm=None))

        # send notification to all families asking them to update
        # their family details
        for family in unconfirmed_families:
            email = EmailTemplate.objects.get(idname='UPDATE_DATA').makeEmail(family, {})[0]
            notification = Notification(family=family, email=email, update_info_dtm=timezone.now())
            notification.save()

# Poll payments which did not recieve callback
class PollQuickpayPaymentsCronJob(CronJobBase):
    RUN_EVERY_MINS = 60 # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'members.poll_quickpayPayments_cronjob'    # a unique code

    def do(self):
        outdated_dtm = timezone.now() - datetime.timedelta(days=14) # Timeout checking payments after 14 days
        payments = Payment.objects.filter(rejected_dtm__isnull=True, confirmed_dtm__isnull=True, payment_type=Payment.CREDITCARD, added__gt=outdated_dtm)

        for payment in payments:
            payment.get_quickpaytransaction().update_status()


# Daily statistics job
class GenerateStatisticsCronJob(CronJobBase):
    RUN_AT_TIMES = ['23:59', ]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'members.generate_statistics_cronjob'  # a unique code


    def do(self):
        timestamp = timezone.now()  # make sure all entries share same timestamp

        # generate general statistics
        dailyStatisticsGeneral = DailyStatisticsGeneral()

        dailyStatisticsGeneral.timestamp = timestamp
        dailyStatisticsGeneral.persons = Person.objects.count()
        dailyStatisticsGeneral.children_male = Person.objects.filter(membertype=Person.CHILD, gender=Person.MALE).count()
        dailyStatisticsGeneral.children_female = Person.objects.filter(membertype=Person.CHILD, gender=Person.FEMALE).count()
        dailyStatisticsGeneral.children = dailyStatisticsGeneral.children_male + dailyStatisticsGeneral.children_female
        dailyStatisticsGeneral.volunteers_male = Person.objects.filter(gender=Person.MALE, volunteer__isnull=False).count()
        dailyStatisticsGeneral.volunteers_female = Person.objects.filter(gender=Person.FEMALE, volunteer__isnull=False).count()
        dailyStatisticsGeneral.volunteers = dailyStatisticsGeneral.volunteers_male + dailyStatisticsGeneral.volunteers_female
        dailyStatisticsGeneral.departments = Department.objects.filter(closed_dtm=None).count()
        dailyStatisticsGeneral.unions = Union.objects.count()
        dailyStatisticsGeneral.waitinglist = WaitingList.objects.all().aggregate(Count('person', distinct=True))['person__count']
        dailyStatisticsGeneral.family_visits = Family.objects.filter(last_visit_dtm__gt=(timestamp-datetime.timedelta(days=1))).count()
        dailyStatisticsGeneral.dead_profiles = Family.objects.filter(last_visit_dtm__lt=(timestamp-datetime.timedelta(days=365))).count()
        dailyStatisticsGeneral.current_activity_participants = Person.objects.filter(member__activityparticipant__activity__end_date__gt=timestamp).distinct().count()
        dailyStatisticsGeneral.activity_participants = Person.objects.filter(member__activityparticipant__activity__isnull=False).distinct().count()

        dailyStatisticsGeneral.save()

        # generate daily department statistics
        departments = Department.objects.filter(closed_dtm=None)
        for department in departments:
            dailyStatisticsDepartment = DailyStatisticsDepartment()

            dailyStatisticsDepartment.timestamp = timestamp
            dailyStatisticsDepartment.department = department
            dailyStatisticsDepartment.active_activities = Activity.objects.filter(department=department, end_date__gt=timestamp).count()
            dailyStatisticsDepartment.activities = Activity.objects.filter(department=department).count()
            dailyStatisticsDepartment.current_activity_participants = 0
            dailyStatisticsDepartment.current_activity_participants_age_avg = 0
            dailyStatisticsDepartment.current_activity_participants_age_min = 0
            dailyStatisticsDepartment.current_activity_participants_age_max = 0
            dailyStatisticsDepartment.activity_participants = 0
            dailyStatisticsDepartment.members = 0
            dailyStatisticsDepartment.waitinglist = WaitingList.objects.filter(department=department).count()
            firstWaitingListItem = WaitingList.objects.filter(department=department).order_by('on_waiting_list_since').first()
            if firstWaitingListItem:
                dailyStatisticsDepartment.waitingtime = timestamp.date() - firstWaitingListItem.on_waiting_list_since
            else:
                dailyStatisticsDepartment.waitingtime = datetime.timedelta(days=0)
            dailyStatisticsDepartment.payments = 0
            dailyStatisticsDepartment.volunteers_male = 0
            dailyStatisticsDepartment.volunteers_female = 0
            dailyStatisticsDepartment.volunteers = 0
            dailyStatisticsDepartment.volunteers_age_avg = 0
            dailyStatisticsDepartment.volunteers_age_min = 0
            dailyStatisticsDepartment.volunteers_age_max = 0

            dailyStatisticsDepartment.save()

# TODO:Find created families/persons, which never clicked the link (spambots etc.)

# TODO:Find families which are about to get deleted from the list and send warning

# TODO:Find Members which are active, but have expired memberships



import datetime

from django.conf import settings
from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.db.models import Q, F

from members.models import (
    EmailItem,
    Notification,
    EmailTemplate,
    ActivityParticipant,
    Payment,
    Person,
    Family,
)


# Send confirmations to Activity signups, which do not have failed payments
class SendActivitySignupConfirmationsCronJob(CronJobBase):
    RUN_EVERY_MINS = 5  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "members.send_activity_signup_confirmation_cronjob"  # a unique code

    def do(self):
        unannounced_signups = ActivityParticipant.objects.exclude(
            notification__isnull=False
        ).filter(payment__accepted_at__isnull=False)

        for announcement in unannounced_signups:
            context = {
                "activity": announcement.activity,
                "person": announcement.person,
                "family": announcement.person.family,
                "union": announcement.activity.department.union,
            }
            emails = EmailTemplate.objects.get(idname="ACT_CONFIRM").makeEmail(
                [announcement.person, announcement.person.family], context
            )
            for email in emails:
                notification = Notification(
                    family=announcement.person.family,
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
        persons = (  # noqa: F841,E261
            Person.objects.filter(municipality__isnull=True)
            .exclude(streetname__exact="")
            .exclude(address_invalid__exact=True)[:50]
        )  # noqa: F841

        for person in persons:
            person.update_dawa_data()


# If it's the first day of the year, make sure to capture all payments that year
class CaptureOutstandingPayments(CronJobBase):
    RUN_AT_TIMES = ["01:00"]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = "members.capture_oustanding_payments"

    def do(self):
        today = datetime.date.today()
        if (today.month, today.day) == (1, 1):
            Payment.capture_oustanding_payments()


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
            Q(confirmed_at__lt=outdated_dtm) | Q(confirmed_at=None)
        ).exclude(
            Q(notification__update_info_dtm__gt=F("confirmed_at"))
            | Q(~Q(notification__update_info_dtm=None), confirmed_at=None)
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
            rejected_at__isnull=True,
            confirmed_at__isnull=True,
            payment_type=Payment.CREDITCARD,
            added_at__gt=outdated_dtm,
        )

        for payment in payments:
            payment.get_quickpaytransaction().update_status()


# Send email to family if payment initiated but not accepted after 3 days
"""
class ReminderEmailPaymentCronJob(CronJobBase):
    RUN_AT_TIMES = ["5:00"]
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
# Following was copied from previous schedule - has to be corrected ;-)
    def do(self):
        unannounced_signups = ActivityParticipant.objects.exclude(
            notification__isnull=False
        ).filter(payment__accepted_at__isnull=False)

        for announcement in unannounced_signups:
            context = {
                "activity": announcement.activity,
                "person": announcement.person,
                "family": announcement.person.family,
                "union": announcement.activity.department.union,
            }
            emails = EmailTemplate.objects.get(idname="ACT_CONFIRM").makeEmail(
                [announcement.person, announcement.person.family], context
            )
            for email in emails:
                notification = Notification(
                    family=announcement.person.family,
                    email=email,
                    anounced_activity_participant=announcement,
                )
                notification.save()
"""

# TODO:Find created families/persons, which never clicked the link (spambots etc.)

# TODO:Find families which are about to get deleted from the list and send warning

# TODO:Find Members which are active, but have expired memberships

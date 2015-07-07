from django_cron import CronJobBase, Schedule
from members.models import EmailItem


class EmailSendCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'members.email_send_cronjob'    # a unique code

    def do(self):
        for curEmail in EmailItem.objects.filter(sent_dtm=None):
            curEmail.send()



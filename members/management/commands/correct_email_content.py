from django.core.management.base import BaseCommand
from members.models.emailitem import EmailItem
from django.db.models import Q


class Command(BaseCommand):
    help = "Update Email content to avoid special characters like curly brackets"

    def handle(self, *args, **options):
        print(f"Starting: {help}")
        for email in EmailItem.objects.filter(
            Q(subject__contains="{") | Q(subject__contains="}")
        ):
            print(f"Correcting subject: {email.subject}")
            email.subject = email.subject.replace("{", "").replace("}", "")
            email.save()

        for email in EmailItem.objects.filter(
            Q(body_html__contains="{") | Q(body_html__contains="}")
        ):
            print(f"Correcting body_html:\n{email.body_html}\n")
            email.body_html = email.body_html.replace("{", "").replace("}", "")
            email.save()

        for email in EmailItem.objects.filter(
            Q(body_text__contains="{") | Q(body_text__contains="}")
        ):
            print(f"Correcting body_text:\n{email.body_text}\n")
            email.body_text = email.body_text.replace("{", "").replace("}", "")
            email.save()
        print("Finished")

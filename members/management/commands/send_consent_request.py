from django.core.management.base import BaseCommand
from django.utils import timezone

from members.models.emailtemplate import EmailTemplate
from members.models.family import Family
from members.models.person import Person


class Command(BaseCommand):
    help = "This command sends a one time anonymization warning if the user has not consented."

    def handle(self, *args, **options):
        for family in Family.objects.filter(
            temp_anonymization_warning_sent_at__isnull=True
        ):
            send_consent_email = True
            email_consent_person = None
            for person in family.get_persons():
                if person.consent_at:
                    send_consent_email = False
                try:
                    email_consent_person = Person.objects.filter(
                        email=family.email
                    ).first()
                except Person.DoesNotExist:
                    email_consent_person = Person.objects.filter(family=family).first()

            if send_consent_email:
                self.stdout.write(f"Sending consent email to {family.email}")
                context = {
                    "person": email_consent_person,
                }
                EmailTemplate.objects.get(idname="FAM_CONSENT").makeEmail(
                    [family], context
                )
                family.temp_anonymization_warning_sent_at = timezone.now()
                family.save()

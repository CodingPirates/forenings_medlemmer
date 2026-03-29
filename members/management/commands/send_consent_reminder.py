from django.core.management.base import BaseCommand
from django.utils import timezone

from members.models.emailtemplate import EmailTemplate
from members.models.family import Family
from members.models.person import Person


class Command(BaseCommand):
    help = (
        "Send consent/inactivity reminder email to persons who are about one month "
        "away from meeting automatic anonymization criteria (inactive ~1y11m, "
        "no payments in 5 fiscal years). Sends if no reminder was sent yet, or the "
        "last one was more than a year ago. Updates consent_reminder_sent_at on each "
        "notified person. One email per family."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List recipients without sending or updating timestamps",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        candidates = Person.get_consent_reminder_queryset()
        family_ids = candidates.values_list("family_id", flat=True).distinct()

        template = EmailTemplate.objects.get(idname="CONSENT_REMINDER")
        sent_families = 0
        marked_persons = 0

        for family_id in family_ids:
            family = Family.objects.get(pk=family_id)
            family_candidates = candidates.filter(family_id=family_id)
            context_person = Person.objects.filter(
                email=family.email, family=family
            ).first()
            if context_person is None:
                context_person = family_candidates.first()
            if context_person is None:
                context_person = (
                    family.get_first_parent() or family.get_persons().first()
                )

            if dry_run:
                self.stdout.write(
                    f"Would send to family {family.email} (person ids: "
                    f"{list(family_candidates.values_list('id', flat=True))})"
                )
                sent_families += 1
                marked_persons += family_candidates.count()
                continue

            self.stdout.write(f"Sending consent reminder to {family.email}")
            template.makeEmail(
                [family],
                {"person": context_person},
                allow_multiple_emails=True,
            )
            now = timezone.now()
            updated = family_candidates.update(consent_reminder_sent_at=now)
            sent_families += 1
            marked_persons += updated

        self.stdout.write(
            f"Done. Families: {sent_families}, persons marked: {marked_persons}"
        )

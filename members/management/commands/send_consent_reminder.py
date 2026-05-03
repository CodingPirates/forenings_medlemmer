from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
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

        # send reminder if no reminder in last year, and will be anonymized soon
        now = timezone.now()
        one_year_ago = now - timedelta(days=365)
        as_of_reminder = timezone.now().date() + timedelta(
            days=settings.CONSENT_REMINDER_LOOKAHEAD_DAYS
        )

        eligible_family_ids = Family.objects.filter(
            anonymized=False, dont_send_mails=False
        ).values_list("pk", flat=True)

        reminder_due = Q(consent_reminder_sent_at__isnull=True) | Q(
            consent_reminder_sent_at__lt=one_year_ago
        )

        person_base = (
            Person.objects.filter(
                anonymized=False,
                family_id__in=eligible_family_ids,
            )
            .filter(reminder_due)
            .select_related("user", "family")
        )

        candidate_persons = [
            p
            for p in person_base.iterator(chunk_size=500)
            if p.is_anonymization_candidate(as_of_date=as_of_reminder)[0]
        ]

        by_family = defaultdict(list)
        for p in candidate_persons:
            by_family[p.family_id].append(p)

        template = EmailTemplate.objects.get(idname="CONSENT_REMINDER")
        sent_families = 0
        marked_persons = 0

        for family_id, family_candidates in by_family.items():
            family = Family.objects.get(pk=family_id)
            context_person = Person.objects.filter(
                email=family.email, family=family
            ).first()
            if context_person is None:
                context_person = family_candidates[0]

            if dry_run:
                self.stdout.write(
                    f"Would send to family #{family.id} (person ids: "
                    f"{[p.pk for p in family_candidates]})"
                )
                sent_families += 1
                marked_persons += len(family_candidates)
                continue

            self.stdout.write(f"Sending consent reminder to family #{family.id}")
            template.makeEmail(
                receivers=[family],
                context={"person": context_person},
                allow_multiple_emails=True,
            )
            updated = Person.objects.filter(
                pk__in=[p.pk for p in family_candidates]
            ).update(consent_reminder_sent_at=now)
            sent_families += 1
            marked_persons += updated

        self.stdout.write(
            f"Done. Families: {sent_families}, persons marked: {marked_persons}"
        )

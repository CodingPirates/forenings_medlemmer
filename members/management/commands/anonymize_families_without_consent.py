from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from members.models.family import Family
from members.models.person import Person

# run command locally in Docker:
# docker compose run web ./manage.py anonymize_families_without_consent --dry-run


class Command(BaseCommand):
    help = "Batch anonymize families where: 1) No consent given by anyone in family, 2) All persons are anonymization candidates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be anonymized without actually doing it",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output for each family",
        )

    def create_request_with_permission(self):
        """Create a mock request object with anonymize_persons permission"""
        return type(
            "Request",
            (object,),
            {
                "user": type(
                    "User",
                    (object,),
                    {
                        "has_perm": lambda self, perm: perm
                        == "members.anonymize_persons"
                    },
                )()
            },
        )()

    def family_has_no_consent(self, family):
        """Check if no person in the family has given consent"""
        persons = family.get_persons().filter(anonymized=False)
        for person in persons:
            if person.consent is not None:
                return (
                    False,
                    f"Person {person.name} (ID: {person.id}) has given consent",
                )
        return True, ""

    def all_persons_are_candidates(self, family):
        """Check if all non-anonymized persons in the family are anonymization candidates"""
        persons = family.get_persons().filter(anonymized=False)
        if not persons.exists():
            # All persons are already anonymized, family can be anonymized
            return True, ""

        for person in persons:
            is_candidate, reason = person.is_anonymization_candidate(relaxed=True)
            if not is_candidate:
                return (
                    False,
                    f"Person {person.name} (ID: {person.id}) is not a candidate: {reason}",
                )
        return True, ""

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        # Create mock request object with permission
        request = self.create_request_with_permission()

        # Get all non-anonymized families
        families = Family.objects.filter(anonymized=False)

        total_families = families.count()
        self.stdout.write(f"Found {total_families} non-anonymized families to check")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        anonymized_count = 0
        skipped_count = 0
        error_count = 0
        processed_count = 0
        last_progress_time = timezone.now()
        start_time = timezone.now()

        for family in families:
            processed_count += 1

            # Log progress every minute when not in verbose mode
            if not verbose:
                current_time = timezone.now()
                if current_time - last_progress_time >= timedelta(minutes=1):
                    elapsed_minutes = (current_time - start_time).total_seconds() / 60
                    self.stdout.write(
                        f"Progress: {processed_count}/{total_families} families processed "
                        f"({anonymized_count} anonymized, {skipped_count} skipped, {error_count} errors) "
                        f"- {elapsed_minutes:.1f} minutes elapsed"
                    )
                    last_progress_time = current_time
            if verbose:
                self.stdout.write(f"\nChecking family {family.id}...")

            # Check if family has no consent
            no_consent, consent_reason = self.family_has_no_consent(family)
            if not no_consent:
                if verbose:
                    self.stdout.write(f"  Skipped: {consent_reason}")
                skipped_count += 1
                continue

            # Check if all persons are anonymization candidates
            all_candidates, candidate_reason = self.all_persons_are_candidates(family)
            if not all_candidates:
                if verbose:
                    self.stdout.write(f"  Skipped: {candidate_reason}")
                skipped_count += 1
                continue

            # Both conditions met - anonymize the family
            if verbose:
                self.stdout.write(f"  ✓ Eligible for anonymization")
                persons = family.get_persons()
                self.stdout.write(
                    f"  Will anonymize {persons.count()} person(s) and the family"
                )

            if not dry_run:
                try:
                    # Anonymize all non-anonymized persons in the family
                    # Note: person.anonymize() automatically anonymizes the family
                    # when all persons are anonymized
                    persons = family.get_persons().filter(anonymized=False)

                    if persons.exists():
                        for person in persons:
                            person.anonymize(request, relaxed=True)
                            if verbose:
                                self.stdout.write(
                                    f"    Anonymized person {person.id} ({person.name})"
                                )
                    else:
                        # All persons already anonymized, anonymize family directly
                        family.anonymize(request, relaxed=True)
                        if verbose:
                            self.stdout.write(
                                f"    All persons already anonymized, anonymizing family"
                            )

                    # Refresh family to verify it was anonymized
                    family.refresh_from_db()
                    if family.anonymized:
                        anonymized_count += 1
                        if verbose:
                            self.stdout.write(
                                f"  ✓ Successfully anonymized family {family.id}"
                            )
                    else:
                        # This shouldn't happen, but log a warning if it does
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠ Family {family.id} persons anonymized but family not anonymized"
                            )
                        )

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ Error anonymizing family {family.id}: {str(e)}"
                        )
                    )
            else:
                anonymized_count += 1
                if not verbose:
                    self.stdout.write(f"Would anonymize family {family.id}")

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Summary:")
        self.stdout.write(f"  Total families checked: {total_families}")
        if dry_run:
            self.stdout.write(f"  Would anonymize: {anonymized_count}")
        else:
            self.stdout.write(f"  Anonymized: {anonymized_count}")
        self.stdout.write(f"  Skipped: {skipped_count}")
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"  Errors: {error_count}"))

from django.core.management.base import BaseCommand
from members.models.member import Member
from datetime import date


class Command(BaseCommand):
    help = "Fixes member_until for memberships where member_since and member_until are inconsistent (e.g., member_since is 1/1/YYYY and member_until is 31/12/YYYY-1)"

    def handle(self, *args, **options):
        fixed_count = 0
        for member in Member.objects.all():
            if (
                member.member_since
                and member.member_until
                and member.member_since.year > member.member_until.year
            ):
                # Example: member_since=2026-01-01, member_until=2025-12-31
                correct_until = date(member.member_since.year, 12, 31)
                self.stdout.write(
                    f"Fixing member {member} (id={member.id}): member_until {member.member_until} -> {correct_until}"
                )
                member.member_until = correct_until
                member.save()
                fixed_count += 1
        self.stdout.write(self.style.SUCCESS(f"Fixed {fixed_count} memberships."))

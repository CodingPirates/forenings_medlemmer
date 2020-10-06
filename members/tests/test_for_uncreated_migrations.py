from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings


class TestMigrationDiscrepancies(TestCase):
    @override_settings(MIGRATION_MODULES={})
    def test_for_missing_migrations(self):
        """Test for missing migrations; the exit code will be non-zero."""
        output = StringIO()
        try:
            call_command("makemigrations", dry_run=True, check=True, stdout=output)
        except SystemExit:
            self.fail("There are missing migrations:\n %s" % output.getvalue())

from datetime import timedelta
from decimal import Decimal

from django.test import SimpleTestCase
from django.utils import timezone

from members.models.activity import Activity


class TestActivityMinimumPrice(SimpleTestCase):
    def get_activity(self, season_fee):
        return Activity(
            end_date=timezone.now().date() + timedelta(days=1),
            season_fee=season_fee,
        )

    def test_season_activity_minimum_matches_lower_season_fee(self):
        activity = self.get_activity(Decimal("100.00"))

        self.assertEqual(activity.get_min_amount("FORLØB"), Decimal("100.00"))

    def test_season_activity_minimum_defaults_to_150_without_lower_fee(self):
        for season_fee in (None, Decimal("150.00"), Decimal("200.00")):
            with self.subTest(season_fee=season_fee):
                activity = self.get_activity(season_fee)

                self.assertEqual(activity.get_min_amount("FORLØB"), Decimal("150"))

    def test_zero_season_fee_allows_zero_minimum_activity_price(self):
        activity = self.get_activity(Decimal("0.00"))

        self.assertEqual(activity.get_min_amount("FORLØB"), Decimal("0.00"))

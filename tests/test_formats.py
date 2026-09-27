import unittest
from datetime import date
from unittest.mock import AsyncMock, patch

from mijnafvalwijzer_ical_proxy.formats import generate_ical
from mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client import PickupMoment


class TestFormats(unittest.IsolatedAsyncioTestCase):

    @patch("mijnafvalwijzer_ical_proxy.formats.fetch_pickup_moments")
    async def test_generate_ical_basic(self, mock_fetch):
        mock_fetch.return_value = [
            PickupMoment(
                waste_type="gft",
                pickup_date=date(2026, 10, 5),
                description="GFT en etensresten",
            ),
            PickupMoment(
                waste_type="papier",
                pickup_date=date(2026, 10, 8),
                description="Papier",
            ),
        ]

        ical_bytes = await generate_ical("3011AD", "10")
        ical_str = ical_bytes.decode("utf-8")

        self.assertIn("BEGIN:VCALENDAR", ical_str)
        self.assertIn("X-WR-CALNAME:Afvalkalender", ical_str)
        self.assertIn("Afvalinzameling - GFT en etensresten", ical_str)
        self.assertIn("Afvalinzameling - Papier", ical_str)
        self.assertIn("3011AD-10-2026-10-05-gft@mijnafvalwijzer-proxy", ical_str)
        self.assertIn("BEGIN:VALARM", ical_str)

    @patch("mijnafvalwijzer_ical_proxy.formats.fetch_pickup_moments")
    async def test_generate_ical_filtering_types(self, mock_fetch):
        mock_fetch.return_value = [
            PickupMoment(
                waste_type="gft",
                pickup_date=date(2026, 10, 5),
                description="GFT",
            ),
            PickupMoment(
                waste_type="papier",
                pickup_date=date(2026, 10, 8),
                description="Papier",
            ),
        ]

        ical_bytes = await generate_ical("3011AD", "10", include_types=["papier"])
        ical_str = ical_bytes.decode("utf-8")

        self.assertIn("Afvalinzameling - Papier", ical_str)
        self.assertNotIn("Afvalinzameling - GFT", ical_str)

    @patch("mijnafvalwijzer_ical_proxy.formats.fetch_pickup_moments")
    async def test_generate_ical_emojis_and_no_alarm(self, mock_fetch):
        mock_fetch.return_value = [
            PickupMoment(
                waste_type="gft",
                pickup_date=date(2026, 10, 5),
                description="GFT",
            ),
        ]

        ical_bytes = await generate_ical(
            "3011AD",
            "10",
            alarm_hours=None,
            emojis=True,
        )
        ical_str = ical_bytes.decode("utf-8")

        self.assertIn("🍌 Afvalinzameling - GFT", ical_str)
        self.assertNotIn("BEGIN:VALARM", ical_str)


if __name__ == "__main__":
    unittest.main()

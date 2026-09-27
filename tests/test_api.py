import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from mijnafvalwijzer_ical_proxy import app
from mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client import (
    AddressNotFoundError,
    PickupMoment,
)


class TestApiEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client.fetch_pickup_moments")
    def test_ical_endpoint_success(self, mock_fetch):
        mock_fetch.return_value = [
            PickupMoment(
                waste_type="gft",
                pickup_date=date(2026, 10, 5),
                description="GFT",
            ),
        ]

        response = self.client.get("/ical/?postal_code=3011AD&number=10&emojis=true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/calendar", response.headers.get("content-type", ""))
        disposition = response.headers.get("content-disposition", "")
        self.assertIn("afvalkalender_3011AD_10.ics", disposition)
        self.assertIn("BEGIN:VCALENDAR", response.text)
        self.assertIn("🍌 Afvalinzameling - GFT", response.text)

    @patch("mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client.fetch_pickup_moments")
    def test_ical_endpoint_address_not_found(self, mock_fetch):
        mock_fetch.side_effect = AddressNotFoundError("Address not found")

        response = self.client.get("/ical/?postal_code=9999ZZ&number=999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Address not found", response.json()["detail"])

    @patch("mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client.fetch_pickup_moments")
    def test_next_pickup_endpoint_success(self, mock_fetch):
        mock_fetch.return_value = [
            PickupMoment(
                waste_type="gft",
                pickup_date=date(2026, 12, 1),
                description="Groente, Fruit en Tuinafval",
            ),
        ]

        response = self.client.get("/next-pickup/?waste_type=gft&postal_code=3011AD&number=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["waste_type"], "gft")
        self.assertEqual(data["pickup_date"], "2026-12-01")
        self.assertEqual(data["description"], "Groente, Fruit en Tuinafval")

    @patch("mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client.fetch_pickup_moments")
    def test_next_pickup_endpoint_not_found(self, mock_fetch):
        mock_fetch.side_effect = AddressNotFoundError("Address not found")

        response = self.client.get("/next-pickup/?waste_type=gft&postal_code=9999ZZ&number=999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

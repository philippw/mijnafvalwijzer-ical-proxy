import unittest
from datetime import date
from unittest.mock import AsyncMock, patch

from mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client import (
    AddressNotFoundError,
    PickupMoment,
    _convert_date,
    fetch_pickup_moments,
)


class TestMijnafvalwijzerClient(unittest.IsolatedAsyncioTestCase):

    def test_convert_date_regular(self):
        ref = date(2026, 5, 10)
        res = _convert_date("dinsdag 12 mei", reference_date=ref)
        self.assertEqual(res, date(2026, 5, 12))

    def test_convert_date_year_rollover_forward(self):
        # In December, viewing January pickups should be next year
        ref = date(2026, 12, 20)
        res = _convert_date("woensdag 6 januari", reference_date=ref)
        self.assertEqual(res, date(2027, 1, 6))

        # In November, viewing February pickups
        ref_nov = date(2026, 11, 28)
        res_feb = _convert_date("vrijdag 5 februari", reference_date=ref_nov)
        self.assertEqual(res_feb, date(2027, 2, 5))

    def test_convert_date_year_rollover_backward(self):
        # In January, viewing previous December pickups
        ref = date(2026, 1, 5)
        res = _convert_date("maandag 28 december", reference_date=ref)
        self.assertEqual(res, date(2025, 12, 28))

    def test_convert_date_invalid(self):
        self.assertIsNone(_convert_date("invalid date string"))
        self.assertIsNone(_convert_date("dinsdag 12 unknownmonth"))

    def test_pickup_moment_model(self):
        moment = PickupMoment(
            waste_type="gft",
            pickup_date=date(2026, 9, 29),
            description="Groente, Fruit en Tuinafval",
        )
        self.assertEqual(moment.waste_type, "gft")
        self.assertEqual(moment.pickup_date, date(2026, 9, 29))
        self.assertEqual(moment.description, "Groente, Fruit en Tuinafval")

    @patch("mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client.aiohttp.ClientSession")
    async def test_fetch_pickup_moments_success(self, mock_session_cls):
        sample_html = """
        <html>
            <body>
                <a class="wasteInfoIcon textDecorationNone" href="#waste-gft">
                    <span class="afvaldescr">Groente, Fruit en Tuinafval</span>
                    <span class="span-line-break">dinsdag 15 september</span>
                </a>
                <a class="wasteInfoIcon textDecorationNone" href="#waste-papier">
                    <span class="afvaldescr">Papier en karton</span>
                    <span class="span-line-break">donderdag 17 september</span>
                </a>
            </body>
        </html>
        """
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = sample_html

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_cls.return_value.__aenter__.return_value = mock_session

        moments = await fetch_pickup_moments("3011 AD", "1")
        self.assertEqual(len(moments), 2)
        self.assertEqual(moments[0].waste_type, "gft")
        self.assertEqual(moments[0].description, "Groente, Fruit en Tuinafval")
        self.assertEqual(moments[1].waste_type, "papier")

    @patch("mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client.aiohttp.ClientSession")
    async def test_fetch_pickup_moments_address_not_found_404(self, mock_session_cls):
        mock_response = AsyncMock()
        mock_response.status = 404

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_cls.return_value.__aenter__.return_value = mock_session

        with self.assertRaises(AddressNotFoundError):
            await fetch_pickup_moments("9999ZZ", "999")

    @patch("mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client.aiohttp.ClientSession")
    async def test_fetch_pickup_moments_address_not_found_page_message(self, mock_session_cls):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<html><body>Geen gegevens gevonden voor dit adres</body></html>"

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_cls.return_value.__aenter__.return_value = mock_session

        with self.assertRaises(AddressNotFoundError):
            await fetch_pickup_moments("9999ZZ", "999")


if __name__ == "__main__":
    unittest.main()

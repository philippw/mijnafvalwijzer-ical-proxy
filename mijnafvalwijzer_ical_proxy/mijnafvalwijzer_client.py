from datetime import date, datetime
from typing import List, Optional

import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel

from mijnafvalwijzer_ical_proxy.const import DATE_RE, MONTHS

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10)
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AfvalwijzerCalendarProxy/1.0)",
    "Accept-Language": "nl,en;q=0.8",
}


class AddressNotFoundError(Exception):
    pass


class PickupMoment(BaseModel):
    waste_type: str
    pickup_date: date
    description: str


async def fetch_pickup_moments(postal_code: str, number: str, suffix: str = "") -> List[PickupMoment]:
    clean_postal_code = postal_code.replace(" ", "").upper()
    clean_number = str(number).strip()
    clean_suffix = str(suffix).strip()

    url_parts = [clean_postal_code, clean_number]
    if clean_suffix:
        url_parts.append(clean_suffix)
    url = f"https://www.mijnafvalwijzer.nl/nl/{'/'.join(url_parts)}"

    result: List[PickupMoment] = []

    async with aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT) as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise AddressNotFoundError(f"Address {clean_postal_code} {clean_number} {clean_suffix} not found")
            if response.status != 200:
                raise RuntimeError(f"Mijnafvalwijzer returned HTTP {response.status}")

            html_text = await response.text()
            parser = BeautifulSoup(html_text, "html.parser")

            # Check if page returned an address error message
            if "Geen gegevens gevonden" in html_text:
                raise AddressNotFoundError(f"Address {clean_postal_code} {clean_number} {clean_suffix} not found")

            for item in parser.find_all("a", class_=lambda c: c and "wasteInfoIcon" in c):
                href = item.get("href", "")
                waste_type = href.replace("#", "").replace("waste-", "")
                if not waste_type or waste_type == "javascript:void(0);":
                    if item.p and item.p.has_attr("class") and item.p["class"]:
                        waste_type = item.p["class"][0]
                    else:
                        waste_type = "unknown"

                descr_el = item.find("span", class_="afvaldescr")
                description = descr_el.get_text(strip=True).replace("\\,", ",") if descr_el else waste_type

                date_el = item.find("span", class_="span-line-break")
                if not date_el:
                    continue

                pickup_date = _convert_date(date_el.get_text(strip=True))
                if pickup_date is None:
                    continue

                result.append(PickupMoment(
                    waste_type=waste_type,
                    pickup_date=pickup_date,
                    description=description,
                ))

    return result


def _convert_date(date_input: str, reference_date: Optional[date] = None) -> Optional[date]:
    match = DATE_RE.match(date_input.strip())
    if not match:
        return None

    ref = reference_date or date.today()
    day = int(match.group(2))
    month_str = match.group(3).lower()
    month = MONTHS.get(month_str)
    if not month:
        return None

    year = ref.year
    # Handle year rollover when fetching at the end of the year for upcoming months
    if ref.month >= 11 and month <= 2:
        year += 1
    elif ref.month <= 2 and month >= 11:
        year -= 1

    return date(year, month, day)

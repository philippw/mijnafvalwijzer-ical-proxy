from datetime import datetime, timedelta, timezone
from typing import List, Optional

from icalendar import Alarm, Calendar, Event

from mijnafvalwijzer_ical_proxy.const import WASTE_EMOJIS
from mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client import fetch_pickup_moments


async def generate_ical(
    postal_code: str,
    number: str,
    suffix: str = "",
    include_types: Optional[List[str]] = None,
    alarm_hours: Optional[int] = 5,
    emojis: bool = False,
) -> bytes:
    clean_postal_code = postal_code.replace(" ", "").upper()
    clean_number = str(number).strip()
    clean_suffix = str(suffix).strip()

    moments = await fetch_pickup_moments(clean_postal_code, clean_number, clean_suffix)

    if include_types:
        normalized_types = {t.lower().strip() for t in include_types}
        moments = [m for m in moments if m.waste_type.lower() in normalized_types]

    cal = Calendar()
    cal.add("prodid", "-//mijnafvalwijzer-ical-proxy//NL")
    cal.add("version", "2.0")
    cal.add("name", "Afvalkalender")
    cal.add("x-wr-calname", "Afvalkalender")
    cal.add("x-wr-timezone", "Europe/Amsterdam")

    alarm = None
    if alarm_hours is not None and alarm_hours > 0:
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("trigger", value=timedelta(hours=-alarm_hours))

    now_utc = datetime.now(timezone.utc)

    for moment in moments:
        emoji_prefix = f"{WASTE_EMOJIS.get(moment.waste_type.lower(), '🗑️')} " if emojis else ""
        summary = f"{emoji_prefix}Afvalinzameling - {moment.description}"

        uid_suffix = f"-{clean_suffix}" if clean_suffix else ""
        event_uid = (
            f"{clean_postal_code}-{clean_number}{uid_suffix}-"
            f"{moment.pickup_date.isoformat()}-{moment.waste_type}@mijnafvalwijzer-proxy"
        )

        event = Event()
        event.add("uid", event_uid)
        event.add("dtstamp", now_utc)
        event.add("dtstart", moment.pickup_date)
        event.add("dtend", moment.pickup_date + timedelta(days=1))
        event.add("summary", summary)
        event.add("description", moment.description)

        if alarm:
            event.add_component(alarm)

        cal.add_component(event)

    return cal.to_ical()

from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from mijnafvalwijzer_ical_proxy import formats
from mijnafvalwijzer_ical_proxy.const import WasteType
from mijnafvalwijzer_ical_proxy.fastapi import CalendarResponse
from mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client import (
    AddressNotFoundError,
    PickupMoment,
    fetch_pickup_moments,
)

app = FastAPI(
    title="Mijnafvalwijzer iCal Proxy",
    description="Proxy service to generate iCal feeds and query waste collection moments from Mijnafvalwijzer.",
    version="1.0.0",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ical/", response_class=CalendarResponse)
async def generate_ical(
    postal_code: str,
    number: str,
    suffix: Optional[str] = "",
    types: Optional[List[str]] = Query(
        None,
        description="Optional list of waste types to include (e.g. ?types=gft&types=papier or ?types=gft,papier)",
    ),
    alarm_hours: Optional[int] = Query(
        5,
        description="Hours before event to trigger notification. Pass 0 to disable alarm.",
    ),
    emojis: bool = Query(
        False,
        description="Prefix event summary with emoji for waste type",
    ),
):
    try:
        # Support comma-separated types in single query param
        parsed_types = None
        if types:
            parsed_types = []
            for t in types:
                parsed_types.extend([item.strip() for item in t.split(",") if item.strip()])

        content = await formats.generate_ical(
            postal_code=postal_code,
            number=number,
            suffix=suffix or "",
            include_types=parsed_types,
            alarm_hours=alarm_hours if alarm_hours and alarm_hours > 0 else None,
            emojis=emojis,
        )
        return CalendarResponse(
            content=content,
            filename=f"afvalkalender_{postal_code.replace(' ', '')}_{number}.ics",
        )
    except AddressNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=502, detail=f"Failed to fetch schedule: {err}") from err


@app.get("/next-pickup/", response_model=Optional[PickupMoment])
async def next_pickup(
    waste_type: WasteType,
    postal_code: str,
    number: str,
    suffix: Optional[str] = "",
):
    try:
        moments = await fetch_pickup_moments(postal_code, number, suffix or "")
    except AddressNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=502, detail=f"Failed to fetch schedule: {err}") from err

    today = date.today()
    return next(
        (m for m in moments if m.waste_type.lower() == waste_type.value.lower() and m.pickup_date >= today),
        None,
    )

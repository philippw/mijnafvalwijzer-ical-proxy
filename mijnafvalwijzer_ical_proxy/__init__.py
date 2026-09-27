from datetime import datetime
from typing import Optional

from fastapi import FastAPI

from mijnafvalwijzer_ical_proxy import formats
from mijnafvalwijzer_ical_proxy.const import WasteType
from mijnafvalwijzer_ical_proxy.fastapi import CalendarResponse
from mijnafvalwijzer_ical_proxy.mijnafvalwijzer_client import fetch_pickup_moments

app = FastAPI()


@app.get("/ical/", response_class=CalendarResponse)
async def generate_ical(postal_code: str, number: str, suffix: Optional[str] = ""):
    return await formats.generate_ical(postal_code, number, suffix)


@app.get("/next-pickup/")
async def next_pickup(waste_type: WasteType, postal_code: str, number: str, suffix: Optional[str] = ""):
    moments = await fetch_pickup_moments(postal_code, number, suffix)

    now = datetime.now().date()

    moments = filter(lambda m: m.waste_type == waste_type.value, moments)
    moments = list(filter(lambda m: m.pickup_date >= now, moments))
    return moments[0] if len(moments) else {}

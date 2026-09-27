from typing import Any, Mapping, Optional
from fastapi.responses import Response


class CalendarResponse(Response):
    media_type = "text/calendar; charset=utf-8"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Any = None,
        filename: str = "afvalkalender.ics",
    ) -> None:
        response_headers = dict(headers or {})
        response_headers.setdefault("Content-Disposition", f'inline; filename="{filename}"')
        super().__init__(
            content=content,
            status_code=status_code,
            headers=response_headers,
            media_type=media_type,
            background=background,
        )

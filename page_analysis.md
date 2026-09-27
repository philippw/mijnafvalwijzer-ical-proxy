# HTML Source Analysis & Implementation Report

**Target Analyzed**: `https://www.mijnafvalwijzer.nl/nl/3045BT/3/`

---

## 1. Key Findings from the HTML Source

1. **Duplicate Pickup Elements (Responsive Layout)**:
   - **Finding**: The HTML page (~1.3MB) renders duplicate monthly calendar blocks: one set for desktop and another hidden/tabbed set for mobile view (e.g. duplicate `<div id="february-2026">` blocks).
   - **Impact on original code**: The original parser matched all `a.wasteInfoIcon` links blindly across the whole document, causing **duplicate calendar events** to be generated for every pickup day throughout the year.

2. **Non-Calendar Waste Links (Separation Guide / Scheidingswijzer)**:
   - **Finding**: The page footer contains a *"Scheidingsinformatie"* (waste separation info) grid with items like `#waste-minicontainer`, `#waste-restafval`, etc., which have `class="wasteInfoIcon"` but **no dates** (`<span class="span-line-break">` is absent).
   - **Impact on original code**: Would raise `AttributeError` on `item.find("span", {"class": "span-line-break"}).text`.

3. **Year Information & Date rollovers**:
   - **Finding**: Pickup dates are listed without years (e.g., `"woensdag 07 januari"`), while container divs contain explicit year IDs (`id="jaar-2026"` and `id="january-2026"`).
   - **Impact on original code**: Hardcoding `datetime.now().year` caused upcoming January/February pickups viewed in late autumn to be attributed to the current/past year.

4. **DOM Structure & Class Names**:
   - Waste types are referenced via `href="#waste-gft"`, `href="#waste-papier"`, etc.
   - Description text is held in `<span class="afvaldescr">`.
   - Date text is formatted as `<span class="span-line-break">dagnaam dd maand</span>`.

---

## 2. Implemented Code Improvements

| Area | Before | Implemented Improvement |
| :--- | :--- | :--- |
| **Deduplication** | Appended every icon tag found in the document. | Scoped search to `#jaaroverzicht` / `jaar-...` containers and added keyed deduplication `(pickup_date, waste_type)`. |
| **Safety & Crash Prevention** | Assumed `<span class="span-line-break">` and `<p>` always exist. | Checked for date element presence and safely ignored non-date info tiles like separation guide icons. |
| **Year-Rollover Logic** | `date(datetime.now().year, ...)` | `_convert_date` accounts for month transitions around year boundaries (e.g. scraping in Nov/Dec for Jan/Feb). |
| **Output Ordering** | Inserter order (which mixed desktop/mobile duplicates). | Explicitly sorted moments chronologically `(pickup_date, waste_type)`. |
| **Network & Timeouts** | Default unbounded `aiohttp` session. | Configured 10s timeout, browser-like `User-Agent`, and custom `Accept-Language` headers. |
| **Error Handling** | Unhandled 500 crashes on missing addresses. | Raised `AddressNotFoundError` for 404s and *"Geen gegevens gevonden"* messages, mapped to clean HTTP 404 responses. |
| **Calendar Customization** | Hardcoded 5h alarm and static titles. | Added optional `emojis`, `alarm_hours`, and `types` filter query parameters. |

---

## 3. Verification

- **Unit & Parser Tests**: Added in `tests/test_client.py`, `tests/test_formats.py`, and `tests/test_api.py`.
- **Date Conversion**: Verified rollover behavior for end-of-year and start-of-year transitions.

from backend.weather_service import ARCHIVE_URL, FORECAST_URL


def select_weather_url(event_date: str | None) -> str:
    return ARCHIVE_URL if event_date else FORECAST_URL


def parse_eonet_event(raw: dict) -> dict:
    return {
        "id":          raw.get("id"),
        "title":       raw.get("title"),
        "description": raw.get("description"),
        "link":        raw.get("link"),
        "closed":      raw.get("closed"),
        "categories":  raw.get("categories", []),
        "sources":     raw.get("sources", []),
        "geometry":    raw.get("geometry", []),
    }


def deduplicate_events(events: list[dict]) -> list[dict]:
    seen, unique = set(), []
    for e in events:
        if e["id"] not in seen:
            seen.add(e["id"])
            unique.append(e)
    return unique

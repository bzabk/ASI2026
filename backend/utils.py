def extract_map_points(events: list[dict]) -> list[dict]:
    points = {}
    for event in events:
        for geom in event.get("geometry", []):
            coords = geom.get("coordinates", [None, None])
            lon, lat = coords[0], coords[1]
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                continue
            eid = event["id"]
            points[eid] = {
                "id":         eid,
                "title":      event["title"],
                "latitude":   lat,
                "longitude":  lon,
                "event_date": geom.get("date", ""),
            }
    return list(points.values())


def parse_eonet_event(raw: dict) -> dict:
    return {
        "id":       raw.get("id"),
        "title":    raw.get("title"),
        "closed":   raw.get("closed"),
        "geometry": raw.get("geometry", []),
    }


def deduplicate_events(events: list[dict]) -> list[dict]:
    seen, unique = set(), []
    for e in events:
        if e["id"] not in seen:
            seen.add(e["id"])
            unique.append(e)
    return unique

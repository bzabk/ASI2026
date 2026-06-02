from backend.utils import (extract_map_points, parse_eonet_event, deduplicate_events)


def test_parse_eonet_event():
    raw = {
        "id": "EONET_20279",
        "title": "Typhoon Jangmi",
        "description": None,
        "link": "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_20279/geojson",
        "closed": None,
        "date": "2026-05-30T18:00:00Z",
        "magnitudeValue": 65.00,
        "magnitudeUnit": "kts",
        "categories": [
            {
                "id": "severeStorms",
                "title": "Severe Storms"
            }
        ],
        "sources": [
            {
                "id": "JTWC",
                "url": "https://www.metoc.navy.mil/jtwc/products/wp0626.tcw"
            }
        ],
        "geometry": {
            "type": "Point",
            "coordinates": [128.5, 20.1]
        }
    }

    result = parse_eonet_event(raw)

    assert result["id"] == "EONET_20279"
    assert result["title"] == "Typhoon Jangmi"
    assert result["closed"] is None
    assert result["geometry"]["type"] == "Point"
    assert result["geometry"]["coordinates"] == [128.5, 20.1]


def test_deduplicate_events():
    events = [
        {"id": "1"},
        {"id": "2"},
        {"id": "1"},
    ]

    result = deduplicate_events(events)

    assert len(result) == 2


def test_extract_map_points():
    events = [
        {
            "id": "abc",
            "title": "Wildfire",
            "geometry": [
                {
                    "coordinates": [10.0, 20.0],
                    "date": "2025-01-01"
                }
            ]
        }
    ]

    result = extract_map_points(events)

    assert len(result) == 1
    assert result[0]["longitude"] == 10.0
    assert result[0]["latitude"] == 20.0


def test_extract_map_points_invalid_coords():
    events = [{
        "id": "E1",
        "title": "Fire",
        "geometry": [{
        "coordinates": ["not", None],
        "date": "2026-01-01"
        }]
        }]

    result = extract_map_points(events)
    assert result == []

def test_extract_map_points_multiple_geometry():
    events = [{
        "id": "1",
        "title": "Fire",
        "geometry": [
            {"coordinates": [10, 20], "date": "a"},
            {"coordinates": [30, 40], "date": "b"}
        ]
    }]

    result = extract_map_points(events)

    assert result[0]["longitude"] == 30
    assert result[0]["latitude"] == 40

def test_extract_map_points_no_geometry():
    events = [{"id": "1", "title": "Fire"}]

    result = extract_map_points(events)

    assert result == []
def test_deduplicate_empty():
    assert deduplicate_events([]) == []
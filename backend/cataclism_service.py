import logging
import httpx
from backend.database import get_conn
from backend.utils import parse_eonet_event, deduplicate_events, extract_map_points

logger = logging.getLogger(__name__)

class CataclismService:

    async def fetch_events(self) -> list:
        url = "https://eonet.gsfc.nasa.gov/api/v3/events"
        params = {"status": "open", "days": 30, "category": "wildfires"}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
        response.raise_for_status()
        parsed = [parse_eonet_event(e) for e in response.json().get("events", [])]
        logger.info("EONET zwrócił %d zdarzeń pożarowych", len(parsed))
        return parsed

    def save(self, points: list):
        conn = get_conn()
        try:
            with conn.cursor() as cursor:
                for p in points:
                    cursor.execute(
                        """
                        INSERT INTO wildfire_events (id, title, longitude, latitude, event_date)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (p["id"], p["title"], p["longitude"], p["latitude"], p["event_date"]),
                    )
            conn.commit()
        finally:
            conn.close()

    async def archive_events(self):
        events = await self.fetch_events()
        points = extract_map_points(deduplicate_events(events))
        self.save(points)
        logger.info("Archiwizacja zakończona: %d zdarzeń", len(points))
        return {"inserted": len(points), "status": "saved"}

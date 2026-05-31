import httpx
from backend.database import get_conn

class  CataclismService:

    async def fetch_events(self):
        try:
            url = "https://eonet.gsfc.nasa.gov/api/v3/events"

            async with httpx.AsyncClient() as client:
                response = await client.get(url)

            response.raise_for_status()

            data = response.json()

            parsed_events = []
            for event in data.get("events",[]):
                parsed_event = {
                "id": event.get("id"),
                "title": event.get("title"),
                "description": event.get("description"),
                "link": event.get("link"),
                "closed": event.get("closed"),
                "categories": event.get("categories", []),
                "sources": event.get("sources", []),
                "geometry": event.get("geometry", [])
                }
                parsed_events.append(parsed_event)
            return parsed_events

        except Exception as e:
            print("ERROR:", e)
            raise


    def save_events(self, events:list):
        conn = get_conn()
        try:
            with conn.cursor() as cursor:
                for event in events:
                    cursor.execute(
                        """
                        INSERT INTO events (id, title, description, link, closed)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """
                    ,(event["id"],event["title"],event["description"],event["link"],event["closed"]))
            conn.commit()
        finally:
            conn.close()

    def save_categories(self, events: list):

        conn = get_conn()

        try:
            with conn.cursor() as cursor:

                for event in events:
                    for cat in event.get("categories", []):
                        cursor.execute("""
                            INSERT INTO categories (id, title)
                            VALUES (%s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, (
                            cat.get("id"),
                            cat.get("title")
                        ))

                        cursor.execute("""
                            INSERT INTO event_categories (event_id, category_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            event["id"],
                            cat.get("id")
                        ))

            conn.commit()

        finally:
            conn.close()
    def save_sources(self, events: list):

        conn = get_conn()

        try:
            with conn.cursor() as cursor:
                for event in events:
                    for s in event.get("sources", []):
                        cursor.execute("""
                            INSERT INTO sources (id, url)
                            VALUES (%s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, (
                            s.get("id"),
                            s.get("url")
                        ))

                        cursor.execute("""
                            INSERT INTO event_sources (event_id, source_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            event["id"],
                            s.get("id")
                        ))
            conn.commit()
        finally:
            conn.close()

    def save_geometry(self, events: list):
        conn = get_conn()
        try:
            with conn.cursor() as cursor:
                for event in events:
                    for g in event.get("geometry", []):
                        coords = g.get("coordinates", [None, None])
                        cursor.execute("""
                            INSERT INTO event_geometry (event_id, geometry_type,longitude,latitude,event_date,magnitude_value,
                                magnitude_unit)
                            VALUES (%s, %s,%s, %s,%s, %s,%s)
                            ON CONFLICT (event_id, event_date) DO NOTHING
                        """,(event["id"],g["type"],coords[0],coords[1],g["date"],g["magnitudeValue"],g["magnitudeUnit"]))
            conn.commit()
        finally:
            conn.close()

    async def sync_events(self):
        events = await self.fetch_events()
        self.save_events(events)
        self.save_categories(events)
        self.save_geometry(events)
        self.save_sources(events)

        return {
            "inserted": len(events),
            "status": "synced"
        }
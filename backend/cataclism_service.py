import httpx

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

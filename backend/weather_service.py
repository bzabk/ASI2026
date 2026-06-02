import logging
import httpx

logger = logging.getLogger(__name__)

ARCHIVE_URL  = "https://archive-api.open-meteo.com/v1/archive"
DAILY_FIELDS = "temperature_2m_max,precipitation_sum,wind_speed_10m_max,shortwave_radiation_sum"


class WeatherService:

    async def get_weather_info(self, latitude: float, longitude: float, event_date: str) -> dict:
        day = event_date[:10]
        params = {
            "latitude":   latitude,
            "longitude":  longitude,
            "daily":      DAILY_FIELDS,
            "timezone":   "auto",
            "start_date": day,
            "end_date":   day,
        }
        logger.info("Fetching archive weather lat=%s lon=%s date=%s", latitude, longitude, day)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(ARCHIVE_URL, params=params)
            resp.raise_for_status()
        return resp.json()

    async def get_temperature_history(self, latitude: float, longitude: float, start_date: str, end_date: str) -> dict:
        params = {
            "latitude":   latitude,
            "longitude":  longitude,
            "daily":      "temperature_2m_max",
            "timezone":   "auto",
            "start_date": start_date,
            "end_date":   end_date,
        }
        logger.info("Fetching temperature history lat=%s lon=%s %s..%s", latitude, longitude, start_date, end_date)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(ARCHIVE_URL, params=params)
            resp.raise_for_status()
        data = resp.json().get("daily", {})
        return {"dates": data.get("time", []), "temperatures": data.get("temperature_2m_max", [])}

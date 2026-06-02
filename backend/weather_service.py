import logging
from datetime import date
import httpx

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CURRENT_FIELDS = "temperature_2m,precipitation,wind_speed_10m,shortwave_radiation"


class WeatherService:

    async def get_weather_info(self, latitude: float, longitude: float) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": CURRENT_FIELDS,
            "timezone": "auto",
        }
        logger.info("Fetching weather for lat=%s lon=%s", latitude, longitude)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
        return resp.json()

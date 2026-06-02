import asyncio
import logging
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException
from backend.weather_service import WeatherService

logger = logging.getLogger(__name__)
router = APIRouter()
_weather = WeatherService()


@router.get("/weather")
async def get_weather(latitude: float, longitude: float, event_date: str):
    try:
        day = event_date[:10]
        start = (date.fromisoformat(day) - timedelta(days=30)).isoformat()
        end = date.today().isoformat()

        metrics, history = await asyncio.gather(
            _weather.get_weather_info(latitude, longitude, event_date),
            _weather.get_temperature_history(latitude, longitude, start, end),
        )
        return {
            "daily":   metrics.get("daily", {}),
            "history": history,
        }
    except Exception as e:
        logger.error("Weather fetch failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

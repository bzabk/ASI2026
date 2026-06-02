import logging
from fastapi import APIRouter, HTTPException
from backend.weather_service import WeatherService

logger = logging.getLogger(__name__)
router = APIRouter()
_weather = WeatherService()


@router.get("/weather")
async def get_weather(latitude: float, longitude: float, event_date: str):
    try:
        return await _weather.get_weather_info(latitude, longitude, event_date)
    except Exception as e:
        logger.error("Weather fetch failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/weather/history")
async def get_weather_history(latitude: float, longitude: float, start_date: str, end_date: str):
    try:
        return await _weather.get_temperature_history(latitude, longitude, start_date, end_date)
    except Exception as e:
        logger.error("Weather history fetch failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

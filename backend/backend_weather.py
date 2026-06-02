import logging
from fastapi import APIRouter, HTTPException
from backend.weather_service import WeatherService

logger = logging.getLogger(__name__)
router = APIRouter()
_weather = WeatherService()


@router.get("/weather")
async def get_weather(latitude: float, longitude: float):
    try:
        return await _weather.get_weather_info(latitude, longitude)
    except Exception as e:
        logger.error("Weather fetch failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

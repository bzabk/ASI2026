from fastapi import FastAPI, Query, HTTPException
from backend.weather_service import WeatherService

app = FastAPI()
weather = WeatherService()


@app.get("/weather")
async def get_weather(latitude: float,longitude: float,start_date: str,end_date: str):
    try:
        return await weather.get_weather_info(latitude, longitude, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

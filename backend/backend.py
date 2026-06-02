import logging
from fastapi import FastAPI
from backend.backend_cataclism import router as cataclism_router
from backend.backend_weather import router as weather_router
from backend.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
init_db()
app.include_router(cataclism_router)
app.include_router(weather_router)

import logging
from fastapi import APIRouter
from backend.cataclism_service import CataclismService
from backend.utils import extract_map_points

logger = logging.getLogger(__name__)
router = APIRouter()
c_service = CataclismService()


@router.get("/fires", response_model=list[dict])
async def get_fires():
    try:
        events = await c_service.fetch_events()
        points = extract_map_points(events)
        c_service.save(points)
        return points
    except Exception as e:
        logger.error("Błąd pobierania pożarów z EONET: %s", e)
        raise



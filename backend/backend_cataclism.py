import logging
from fastapi import APIRouter
from backend.cataclism_service import CataclismService
from backend.utils import extract_map_points

logger = logging.getLogger(__name__)
router = APIRouter()
c_service = CataclismService()


@router.get("/fires")
async def get_fires():
    events = await c_service.fetch_events()
    return extract_map_points(events)


@router.post("/archive")
async def archive():
    result = await c_service.archive_events()
    logger.info("Archive done: %s", result)
    return result

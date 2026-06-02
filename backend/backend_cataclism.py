import logging
from fastapi import APIRouter
from backend.cataclism_service import CataclismService
from backend.utils import extract_map_points

logger = logging.getLogger(__name__)
router = APIRouter()
c_service = CataclismService()


@router.get("/disasters/map")
async def get_disasters_map():
    events = await c_service.fetch_events()
    return extract_map_points(events)


@router.post("/refresh-dis")
async def refresh_dis():
    result = await c_service.sync_events()
    logger.info("Sync done: %s", result)
    return result

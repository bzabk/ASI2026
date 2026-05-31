from fastapi import APIRouter
from backend.cataclism_service import CataclismService
router = APIRouter()

c_service = CataclismService()

@router.get("/test-dis")
async def test_dis():
    return await c_service.fetch_events()

@router.post("/refresh-dis")
async def refresh_dis():
    events = await c_service.fetch_events()

    c_service.save_events(events)
    return {"status": "done"}
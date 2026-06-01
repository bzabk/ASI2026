from fastapi import APIRouter
from backend.cataclism_service import CataclismService
from backend.database import get_conn
router = APIRouter()

c_service = CataclismService()

@router.get("/disasters")
def get_disasters():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT id, title, description, link, closed
             FROM events LIMIT 100
             """)
            rows = cursor.fetchall()

        return rows
    finally:
        conn.close()
@router.get("/disasters/categories")
def get_categories():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT *
             FROM categories
             """)
            rows = cursor.fetchall()

        return rows
    finally:
        conn.close()
@router.get("/disasters/event_categories")
def get_categories():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT *
             FROM event_categories
             """)
            rows = cursor.fetchall()

        return rows
    finally:
        conn.close()
@router.get("/disasters/sources")
def get_categories():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT *
             FROM sources
             """)
            rows = cursor.fetchall()

        return rows
    finally:
        conn.close()
@router.get("/disasters/event_sources")
def get_categories():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT *
             FROM event_sources
             """)
            rows = cursor.fetchall()

        return rows
    finally:
        conn.close()
@router.get("/disasters/geometry")
def get_geometry():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT *
             FROM event_geometry
             """)
            rows = cursor.fetchall()

        return rows
    finally:
        conn.close()
@router.post("/refresh-dis")
async def refresh_dis():
    await c_service.sync_events()
    return {"status": "done"}

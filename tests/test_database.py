from unittest.mock import MagicMock, patch
from backend.cataclism_service import CataclismService
from backend.database import get_conn


def test_save_to_db():
    mock_cursor = MagicMock()

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch("backend.cataclism_service.get_conn", return_value=mock_conn):

        service = CataclismService()

        service.save([
            {
                "id": "E1",
                "title": "Fire",
                "longitude": 10,
                "latitude": 20,
                "event_date": "2026-01-01"
            }
        ])

    assert mock_cursor.execute.called
    assert mock_conn.commit.called

def test_db_basic_connection_and_insert():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM wildfire_events")

    cur.execute("""
        INSERT INTO wildfire_events (id, title, longitude, latitude, event_date)
        VALUES ('T1', 'Test', 10, 20, '2026-01-01')
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM wildfire_events WHERE id='T1'")
    count = cur.fetchone()[0]

    conn.close()

    assert count == 1



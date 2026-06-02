from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest
from backend.backend import app

client = TestClient(app)

class MockResponse:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        return None

    def json(self):
        return self._json


class MockClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, *args, **kwargs):
        return self._response


def test_disasters_map_route():
    fake_response = MockResponse({
        "events": [
            {
                "id": "E1",
                "title": "Test Fire",
                "geometry": [
                    {
                        "type": "Point",
                        "coordinates": [10.0, 20.0],
                        "date": "2026-01-01T00:00:00Z"
                    }
                ]
            }
        ]
    })

    with patch("httpx.AsyncClient", return_value=MockClient(fake_response)):
        response = client.get("/disasters/map")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert data[0]["id"] == "E1"
    assert data[0]["latitude"] == 20.0
    assert data[0]["longitude"] == 10.0


def test_refresh_dis_route():
    fake_response = MockResponse({
        "events": [
            {
                "id": "E1",
                "title": "Test",
                "geometry": []
            }
        ]
    })

    with    patch("httpx.AsyncClient", return_value=MockClient(fake_response)), \
            patch("backend.cataclism_service.get_conn"):

            response = client.post("/refresh-dis")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "synced"
    assert "inserted" in data

@pytest.mark.asyncio
async def test_weather_fetch():
    fake_response = MockResponse({
        "daily": {
            "temperature_2m_max": [20],
            "time": ["2026-01-01"]
        }
    })

    with patch("httpx.AsyncClient", return_value=MockClient(fake_response)):
        from backend.weather_service import WeatherService

        ws = WeatherService()
        result = await ws.get_weather_info(10, 20, "2026-01-01")

    assert "daily" in result


@pytest.mark.asyncio
async def test_weather_history():
    fake_response = MockResponse({
        "daily": {
            "time": ["2026-01-01"],
            "temperature_2m_max": [25]
        }
    })

    with patch("httpx.AsyncClient", return_value=MockClient(fake_response)):
        from backend.weather_service import WeatherService

        ws = WeatherService()
        result = await ws.get_temperature_history(
            10, 20, "2026-01-01", "2026-01-02"
        )

    assert "dates" in result
    assert "temperatures" in result
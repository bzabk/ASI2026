import logging

import requests

logger = logging.getLogger(__name__)


class BackendClient:
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def get_events(self, category: str | None = None, limit: int = 100) -> list[dict]:
        params: dict = {"limit": limit}
        if category:
            params["category"] = category
        try:
            resp = requests.get(
                f"{self._base_url}/events",
                params=params,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            logger.error("Timeout przy /events (category=%s)", category)
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP %s przy /events: %s", e.response.status_code, e.response.text)
        except requests.exceptions.RequestException as e:
            logger.error("Błąd połączenia z backendem: %s", e)
        return []

    def get_weather(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
    ) -> dict | None:
        try:
            resp = requests.get(
                f"{self._base_url}/weather",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            logger.error("Timeout przy /weather (lat=%s, lon=%s)", lat, lon)
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP %s przy /weather: %s", e.response.status_code, e.response.text)
        except requests.exceptions.RequestException as e:
            logger.error("Błąd połączenia z backendem: %s", e)
        return None

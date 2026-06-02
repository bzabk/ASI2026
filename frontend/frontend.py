import logging
import os

import pydeck as pdk
import requests
import streamlit as st

logger = logging.getLogger(__name__)
API_URL = os.getenv("API_URL", "http://localhost:8000")


class Main:

    def __init__(self):
        st.set_page_config(page_title="Mapa Kataklizmów", layout="wide")

    def run(self) -> None:
        st.title("Mapa pożarów")
        self._prepare_map()
        self._prepare_metrics()

    def _prepare_map(self) -> None:

        if st.button("Odśwież dane z API"):
            with st.spinner("Pobieranie danych..."):
                try:
                    resp = requests.post(f"{API_URL}/refresh-dis", timeout=60)
                    resp.raise_for_status()
                    result = resp.json()
                    st.success(f"Zsynchronizowano {result.get('inserted', '?')} zdarzeń")
                except Exception as e:
                    logger.error("Refresh failed: %s", e)
                    st.error(f"Błąd odświeżania: {e}")

        points = []
        try:
            resp = requests.get(f"{API_URL}/disasters/map", timeout=10)
            resp.raise_for_status()
            points = resp.json()
        except Exception as e:
            logger.error("Map data fetch failed: %s", e)
            st.warning(f"Nie można pobrać danych mapy: {e}")

        if not points:
            st.info("Brak danych — kliknij 'Odśwież dane z API' aby pobrać zdarzenia.")

        layer = pdk.Layer(
            "ScatterplotLayer",
            id="wildfires",
            data=points,
            get_position="[longitude, latitude]",
            get_color=[255, 80, 0, 210],
            get_radius=20000,
            radius_min_pixels=3,
            radius_max_pixels=6,
            pickable=True,
        )

        chart = st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.5),
                tooltip={"text": "{title}\n{event_date}"},
            ),
            on_select="rerun",
            selection_mode="single-object",
        )

        selected = (chart.selection.objects or {}).get("wildfires", [])
        if selected:
            point = selected[0]
            st.session_state["selected_point"] = {
                "lat": point.get("latitude"),
                "lon": point.get("longitude"),
                "title": point.get("title", ""),
            }
        elif "selected_point" not in st.session_state:
            st.session_state["selected_point"] = None

    def _prepare_metrics(self) -> None:
        st.subheader("Warunki pogodowe")
        point = st.session_state.get("selected_point")

        if not point:
            st.info("Kliknij pożar na mapie aby zobaczyć aktualne warunki pogodowe.")
            return

        st.caption(f"Lokalizacja: **{point['title']}**")
        try:
            resp = requests.get(
                f"{API_URL}/weather",
                params={"latitude": point["lat"], "longitude": point["lon"]},
                timeout=10,
            )
            resp.raise_for_status()
            current = resp.json().get("current", {})

            temp = current.get("temperature_2m")
            precip = current.get("precipitation")
            wind = current.get("wind_speed_10m")
            radiation = current.get("shortwave_radiation")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Temperatura", f"{temp} °C" if temp is not None else "—")
            with col2:
                st.metric("Opady", f"{precip} mm" if precip is not None else "—")
            with col3:
                st.metric("Wiatr", f"{wind} km/h" if wind is not None else "—")
            with col4:
                st.metric("Nasłonecznienie", f"{radiation} W/m²" if radiation is not None else "—")
        except Exception as e:
            logger.error("Weather metrics error: %s", e)
            st.warning(f"Nie można pobrać danych pogodowych: {e}")

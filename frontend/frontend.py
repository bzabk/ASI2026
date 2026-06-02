import logging
import os
from datetime import date, timedelta

import altair as alt
import pandas as pd
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
        st.caption("Mapa prezentuje miejsca pożarów z ostatnich 30 dni.")

        if st.button("Odśwież dane z API"):
            with st.spinner("Pobieranie danych..."):
                try:
                    resp = requests.post(f"{API_URL}/refresh-dis", timeout=60)
                    resp.raise_for_status()
                    result = resp.json()
                    st.success(f"Załadowano {result.get('inserted', '?')} zdarzeń")
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
                "lat":        point.get("latitude"),
                "lon":        point.get("longitude"),
                "title":      point.get("title", ""),
                "event_date": point.get("event_date", ""),
            }
        elif "selected_point" not in st.session_state:
            st.session_state["selected_point"] = None

    def _prepare_metrics(self) -> None:
        st.subheader("Warunki pogodowe")
        point = st.session_state.get("selected_point")

        if not point:
            st.info("Kliknij pożar na mapie aby zobaczyć aktualne warunki pogodowe.")
            return

        event_date = point.get("event_date", "")
        date_label = event_date[:10] if event_date else ""
        st.caption(f"Lokalizacja: **{point['title']}**" + (f" · {date_label}" if date_label else ""))
        try:
            params = {"latitude": point["lat"], "longitude": point["lon"]}
            if event_date:
                params["event_date"] = event_date
            resp = requests.get(f"{API_URL}/weather", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            d = data.get("daily", {})
            temp      = (d.get("temperature_2m_max") or [None])[0]
            precip    = (d.get("precipitation_sum") or [None])[0]
            wind      = (d.get("wind_speed_10m_max") or [None])[0]
            radiation = (d.get("shortwave_radiation_sum") or [None])[0]
            rad_unit  = "MJ/m²"

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Temperatura", f"{temp} °C" if temp is not None else "—")
            with col2:
                st.metric("Opady", f"{precip} mm" if precip is not None else "—")
            with col3:
                st.metric("Wiatr", f"{wind} km/h" if wind is not None else "—")
            with col4:
                st.metric("Nasłonecznienie", f"{radiation} {rad_unit}" if radiation is not None else "—")
        except Exception as e:
            logger.error("Weather metrics error: %s", e)
            st.warning(f"Nie można pobrać danych pogodowych: {e}")

        self._prepare_temperature_chart(point)

    def _prepare_temperature_chart(self, point: dict) -> None:
        event_date = point.get("event_date", "")
        if not event_date:
            return
        try:
            start = (date.fromisoformat(event_date[:10]) - timedelta(days=30)).isoformat()
            end = date.today().isoformat()
            resp = requests.get(
                f"{API_URL}/weather/history",
                params={"latitude": point["lat"], "longitude": point["lon"], "start_date": start, "end_date": end},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            dates = data.get("dates", [])
            temps = data.get("temperatures", [])
            if dates and temps:
                df = pd.DataFrame({"date": pd.to_datetime(dates), "Temperatura (°C)": temps})
                fire_dt = pd.to_datetime(event_date[:10])

                temp_line = alt.Chart(df).mark_line(color="#ff5000").encode(
                    x=alt.X("date:T", title="Data"),
                    y=alt.Y("Temperatura (°C):Q", title="Temperatura (°C)"),
                    tooltip=["date:T", "Temperatura (°C):Q"],
                )
                fire_rule = alt.Chart(
                    pd.DataFrame({"fire": [fire_dt]})
                ).mark_rule(color="red", strokeDash=[6, 4], strokeWidth=2).encode(
                    x="fire:T",
                )

                st.subheader("Temperatura dzienna")
                st.caption(f"Zakres: {start} → {end}  ·  — czerwona linia = moment pożaru")
                st.altair_chart(temp_line + fire_rule, use_container_width=True)
        except Exception as e:
            logger.error("Temperature chart error: %s", e)
            st.warning(f"Nie można pobrać historii temperatury: {e}")

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

st.set_page_config(page_title="Mapa Kataklizmów", layout="wide")
st.title("Mapa pożarów")


def prepare_map():
    st.caption("Mapa prezentuje miejsca pożarów z ostatnich 30 dni.")

    # getting wildfires points
    points = []
    try:
        resp = requests.get(f"{API_URL}/fires", timeout=10)
        resp.raise_for_status()
        points = resp.json()
    except Exception as e:
        logger.error("Błąd pobierania danych mapy: %s", e)
        st.warning(f"Nie można pobrać danych mapy: {e}")

    if not points:
        st.info("Brak danych — kliknij 'Odśwież dane z API' aby pobrać zdarzenia.")
    #map settings
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
    #hover on click
    selected = (chart.selection.objects or {}).get("wildfires", [])
    if selected:
        p = selected[0]
        st.session_state["selected_point"] = {
            "lat":        p.get("latitude"),
            "lon":        p.get("longitude"),
            "title":      p.get("title", ""),
            "event_date": p.get("event_date", ""),
        }
    elif "selected_point" not in st.session_state:
        st.session_state["selected_point"] = None


def prepare_metrics():
    st.subheader("Warunki pogodowe")
    point = st.session_state.get("selected_point")

    if not point:
        st.info("Kliknij pożar na mapie aby zobaczyć aktualne warunki pogodowe.")
        return

    event_date = point.get("event_date", "")
    date_label = event_date[:10] if event_date else ""
    st.caption(f"Lokalizacja: **{point['title']}**" + (f" · {date_label}" if date_label else ""))

    try:
        resp = requests.get(
            f"{API_URL}/weather",
            params={"latitude": point["lat"], "longitude": point["lon"], "event_date": event_date},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        d = data.get("daily", {})
        temp      = (d.get("temperature_2m_max") or [None])[0]
        precip    = (d.get("precipitation_sum") or [None])[0]
        wind      = (d.get("wind_speed_10m_max") or [None])[0]
        radiation = (d.get("shortwave_radiation_sum") or [None])[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Temperatura", f"{temp} °C" if temp is not None else "—")
        with col2:
            st.metric("Opady", f"{precip} mm" if precip is not None else "—")
        with col3:
            st.metric("Wiatr", f"{wind} km/h" if wind is not None else "—")
        with col4:
            st.metric("Nasłonecznienie", f"{radiation} MJ/m²" if radiation is not None else "—")

        prepare_temperature_chart(point, data.get("history", {}))
    except Exception as e:
        logger.error("Błąd pobierania danych pogodowych: %s", e)
        st.warning(f"Nie można pobrać danych pogodowych: {e}")


def prepare_temperature_chart(point: dict, history: dict):
    event_date = point.get("event_date", "")
    if not event_date:
        return
    try:
        start = (date.fromisoformat(event_date[:10]) - timedelta(days=30)).isoformat()
        end = date.today().isoformat()
        dates = history.get("dates", [])
        temps = history.get("temperatures", [])
        if not dates or not temps:
            return

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
        logger.error("Błąd pobierania historii temperatury: %s", e)
        st.warning(f"Nie można pobrać historii temperatury: {e}")


prepare_map()
prepare_metrics()

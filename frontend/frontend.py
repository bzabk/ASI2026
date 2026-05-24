import pydeck as pdk
import streamlit as st


class Main:

    def __init__(self):
        st.set_page_config(page_title="Mapa Kataklizmów", layout="wide")
        self._selected_cat: str = "wildfires"
        self._limit: int = 100

    def run(self) -> None:
        st.title("Mapa Kataklizmów")

        self._prepare_sidebar()
        self._prepare_metrics()
        self._prepare_map()

    def _prepare_sidebar(self) -> None:
        categories = ["wildfires", "floods", "droughts", "storms"]
        selected_label = st.sidebar.selectbox("Typ kataklizmu", list(categories))
        self._selected_cat = selected_label
        self._limit = st.sidebar.slider("Maks. liczba zdarzeń", 10, 500, 100)

    def _prepare_metrics(self) -> None:
        pass


    def _prepare_map(self) -> None:
        st.subheader("Mapa zdarzeń")
        st.pydeck_chart(
            pdk.Deck(
                initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.5),
            )
        )


from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.api_mag import load_data

GEO_DIR = Path(__file__).resolve().parent.parent / "geojson"
RED = "#ff4b4b"

st.set_page_config(page_title="Map and selectors", layout="wide")
st.title("Map and selectors")

AREA_TYPES = {"Price Areas (EL)": "EL", "Weather Areas": "Weather"}
code = AREA_TYPES[st.radio("Area type", list(AREA_TYPES), horizontal=True)]
st.selectbox("Weather variable", ["temperature", "precipitation"])


@st.cache_data
def load_areas(filename, name_column):
    gdf = gpd.read_file(GEO_DIR / filename)  # GeoJSON is always EPSG:4326
    gdf["map_name"] = gdf[name_column].astype(str)
    return gdf[["map_name", "geometry"]]


def show_map(gdf, values, title, label, code):
    """Draw the coloured map, highlight the stored selection, store new clicks."""
    key = f"map_{code}"

    # Read the click from the previous run *before* building the figure,
    # so the outline changes immediately.
    state = st.session_state.get(key) or {}
    points = state.get("selection", {}).get("points", [])
    if points:
        name = points[0]["location"]
        st.session_state.update(selected_map_area=name, selected_map_area_type=code)
        if code == "EL":
            st.session_state.update(selected_el_area=name, selected_area_number=int(name[-1]))
        else:
            st.session_state["selected_weather_area"] = name

    gdf = gdf.merge(values, on="map_name", how="left")

    def layer(df, **kwargs):
        return go.Choropleth(
            geojson=df.__geo_interface__,
            locations=df["map_name"],
            featureidkey="properties.map_name",
            **kwargs,
        )

    fig = go.Figure(
        layer(
            gdf,
            z=gdf["value"],
            colorscale="Viridis",
            marker={"line": {"color": "#222222", "width": 1}, "opacity": 0.65},
            colorbar={"title": label},
            hovertemplate="%{location}<br>" + label + ": %{z:.2f}<extra></extra>",
        )
    )

    if st.session_state.get("selected_map_area_type") == code:
        chosen = gdf[gdf["map_name"] == st.session_state.get("selected_map_area")]
        if not chosen.empty:
            fig.add_trace(
                layer(
                    chosen,
                    z=[0] * len(chosen),
                    colorscale=[[0, "rgba(255,75,75,0.12)"], [1, "rgba(255,75,75,0.12)"]],
                    showscale=False,
                    marker={"line": {"color": RED, "width": 5}},
                    hoverinfo="skip",
                )
            )

    fig.update_geos(fitbounds="locations", visible=False, showcountries=True, countrycolor="#777777")
    if code == "Weather":
        west, south, east, north = gdf.total_bounds
        lon_padding = (east - west) * 0.05
        lat_padding = (north - south) * 0.05
        fig.update_geos(
            fitbounds=False,
            lonaxis_range=[west - lon_padding, east + lon_padding],
            lataxis_range=[south - lat_padding, north + lat_padding],
        )
    fig.update_layout(title=title, margin={"r": 0, "t": 45, "l": 0, "b": 0}, height=650)
    st.plotly_chart(fig, width="stretch", key=key, on_select="rerun", selection_mode="points")

    if st.session_state.get("selected_map_area_type") == code:
        st.success(f"Selected area: {st.session_state['selected_map_area']}")


if code == "EL":
    gdf = load_areas("electricity_areas.geojson", "budomr")
    mag = load_data()
    months = sorted(mag["Date"].dt.to_period("M").unique())
    start, end = st.select_slider(
        "Select month range",
        options=months,
        value=(months[0], months[-1]),
        format_func=str,
        key="map_price_month_range",
    )
    el = mag[
        mag["Date"].dt.to_period("M").between(start, end) & (mag["Area Type"] == "EL")
    ]
    values = (
        el.assign(map_name="NO " + el["Area Number"].astype(str))
        .groupby("map_name", as_index=False)["Filling Ratio"]
        .mean()
        .rename(columns={"Filling Ratio": "value"})
    )
    show_map(gdf, values, "EL price areas", "Mean filling ratio (%)", code)

else:
    gdf = load_areas("precipitation_areas.geojson", "REGIONNAVN")
    values = gdf[["map_name"]].assign(value=1)
    show_map(gdf, values, "Weather areas", "Area", code)

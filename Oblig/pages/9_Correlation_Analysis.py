import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.title("Correlation Analysis")

required_data = ("selected_data", "meteorological_data")
if not all(key in st.session_state for key in required_data):
    st.info("Select reservoir data and retrieve meteorological data first.")
    st.stop()

if st.session_state.get("plot_area_type") != "EL":
    st.info("Meteorological data is available for EL areas only.")
    st.stop()

weather_options = {
    "Precipitation": ("precipitation", "sum"),
    "Temperature": ("temperature_2m", "mean"),
}
weather_choice = st.radio("Weather variable", list(weather_options), index=0)
weather_column, weekly_aggregation = weather_options[weather_choice]


# Prepare weekly reservoir filling ratios.
reservoir_data = st.session_state["selected_data"][
    ["Date", "Filling Ratio"]
].copy()
reservoir_data["Date"] = pd.to_datetime(
    reservoir_data["Date"]
).dt.tz_localize(None)
reservoir_data["Filling Ratio"] = pd.to_numeric(
    reservoir_data["Filling Ratio"],
    errors="coerce",
)
reservoir_data = reservoir_data.dropna(subset=["Filling Ratio"])

reservoir_weeks = reservoir_data["Date"].dt.to_period("W-SUN")
reservoir_weekly = reservoir_data["Filling Ratio"].groupby(
    reservoir_weeks
).mean()


# Weight weather observations by the number of sampled locations per grid cell.
weather_data = st.session_state["meteorological_data"][
    ["date", weather_column, "weight"]
].copy()
weather_data["date"] = pd.to_datetime(
    weather_data["date"]
).dt.tz_localize(None)
weather_data = weather_data.dropna(
    subset=[weather_column, "weight"]
)
weather_data["weighted_value"] = (
    weather_data[weather_column] * weather_data["weight"]
)

weather_by_hour = weather_data.groupby("date").agg(
    weighted_value=("weighted_value", "sum"),
    weight=("weight", "sum"),
)
weather_by_hour["value"] = (
    weather_by_hour["weighted_value"] / weather_by_hour["weight"]
)

weather_weeks = weather_by_hour.index.to_period("W-SUN")
weather_weekly = weather_by_hour["value"].groupby(
    weather_weeks
).agg(weekly_aggregation)


# Compare only weeks that are available in both data sources.
weekly_data = pd.concat(
    [reservoir_weekly, weather_weekly],
    axis=1,
    join="inner",
).dropna()
weekly_data.columns = ["Filling Ratio", weather_choice]

if len(weekly_data) < 3:
    st.info("At least three overlapping weeks are required.")
    st.stop()

window = st.slider(
    "Sliding window (weeks)",
    min_value=3,
    max_value=min(52, len(weekly_data)),
    value=min(12, min(52, len(weekly_data))),
)
correlation = weekly_data["Filling Ratio"].rolling(
    window=window,
    center=True,
).corr(
    weekly_data[weather_choice]
)

fig = go.Figure(
    go.Scatter(
        x=weekly_data.index.to_timestamp(),
        y=correlation,
        mode="lines",
        name="Rolling correlation",
    )
)
fig.add_hline(
    y=0,
    line_dash="dot",
    line_color="gray",
)
fig.update_layout(
    title=f"Filling Ratio and {weather_choice}: {window}-week correlation",
    xaxis_title="Week",
    yaxis_title="Correlation",
)
fig.update_yaxes(range=[-1, 1])
st.plotly_chart(fig, width="stretch")

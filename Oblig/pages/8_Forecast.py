from collections import deque

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from river import linear_model, preprocessing

from modules.api_mag import load_data


# Defining forecasting function using lag-based machine learning.
def forecast_filling(
    df,
    area_type,
    area_number,
    horizon=12,
    train_start=None,
    train_end=None,
    resolution=1,
    lags=None,
    model=None,
):

    # Defining Filling Ratio from df_mag to be the only relevant target.
    target = "Filling Ratio"

    # Defining resolution options to be 1/2/3/4 week(s) or one calendar
    # month ("M").
    # Resolution options are now 1 or 2 weeks, or one calendar month ("M").
    if resolution != "M" and resolution not in (1, 2):
        raise ValueError('resolution must be 1, 2 or "M".')

    # Defining step size based on resolution such that lags can be
    # correctly defined.
    # Lags are counted in steps, not explicitly weeks, i.e. max_lag=52 is
    # only equal to one year if step size = resolution = 1 week. Some math
    # is therefore necessary to account for the resolution options.
    weeks_per_step = 52 / 12 if resolution == "M" else resolution
    step = pd.DateOffset(months=1) if resolution == "M" else pd.Timedelta(weeks=resolution)
    if lags is None:
        lags = (1, 2, 3, round(52 / weeks_per_step))  # last lag = one year back
    max_lag = max(lags)

    # Selecting region based on user input, selecting most recent data.
    # The whole series is kept here. train_start and train_end are applied
    # further down, so the latest observation is still available as the
    # forecast start.
    mask = (df["Area Type"] == area_type) & (df["Area Number"] == area_number)
    data = df.loc[mask, ["Date", target]].dropna().sort_values("Date").copy()
    data["Date"] = pd.to_datetime(data["Date"])

    # Selecting training data from df_mag based on resolution. For
    # resolutions with multiple observations, the last observation is
    # taken. Averaging mutiple observations into one training point (to
    # capture more training data) can cause the forecast to shift.
    if resolution == "M":
        data = data.groupby(data["Date"].dt.to_period("M")).tail(1)  # last observation per month
    else:
        data = data.iloc[::-resolution].iloc[::-1]  # every k-th week, counted back from the latest
    data = data.reset_index(drop=True)
    if len(data) <= max_lag:
        raise ValueError("Not enough history for the chosen lags and resolution.")

    # Using River to set up model.
    # clone() returns an untrained copy, so every call starts from scratch.
    if model is None:
        model = preprocessing.StandardScaler() | linear_model.LinearRegression()
    else:
        model = model.clone()

    # Defining features function. buffer is the deque containing n = max_lag
    # observations. The block iterates over each lag and copies relevant
    # values into the feature dictionary for use in later training.
    # Each value's position in the year is defined as part of an annual
    # cycle (thus sine/cosine). This eases season handling.
    def make_features(buffer, date):
        x = {f"lag{lag}": buffer[-lag] for lag in lags}
        year_pos = 2 * np.pi * date.dayofyear / 365.25  # radians because math
        x["season_sin"] = np.sin(year_pos)
        x["season_cos"] = np.cos(year_pos)
        return x

    # Finding the rows to train on: targets between train_start and train_end
    # (None = no limit). Their lag values may come from before train_start.
    y = data[target].to_numpy()
    dates = data["Date"]
    in_window = pd.Series(True, index=data.index)
    if train_start is not None:
        in_window &= dates >= pd.Timestamp(train_start)
    if train_end is not None:
        in_window &= dates <= pd.Timestamp(train_end)
    rows = np.flatnonzero(in_window.to_numpy())
    if rows.size == 0 or max(rows[0], max_lag) > rows[-1]:
        raise ValueError("Not enough history in the training window for the chosen lags and resolution.")
    first, last = max(rows[0], max_lag), rows[-1]

    # Training one step at a time using .learn_one() and data from features.
    # The deque holds the latest max_lag values; each append drops the oldest.
    buffer = deque(y[first - max_lag:first], maxlen=max_lag)
    for i in range(first, last + 1):
        model.learn_one(make_features(buffer, dates.iloc[i]), y[i])
        buffer.append(y[i])

    # Moving the buffer on to the latest observation without learning, so the
    # forecast starts there and not at train_end.
    for value in y[last + 1:]:
        buffer.append(value)

    # Forecasting recursively. Each prediction becomes the newest lag value.
    # The forecast runs from the latest observation to forecast_end.
    forecast_start = dates.iloc[-1]
    forecast_end = forecast_start + pd.Timedelta(weeks=horizon)
    if forecast_start + step > forecast_end:
        raise ValueError("horizon is shorter than one step of the chosen resolution.")
    out_dates, preds = [], []
    h = 1
    while forecast_start + h * step <= forecast_end:
        date = forecast_start + h * step
        y_hat = model.predict_one(make_features(buffer, date))
        buffer.append(y_hat)
        out_dates.append(date)
        preds.append(y_hat)
        h += 1

    return pd.DataFrame({"Date": out_dates, "Forecast": preds})


st.title("Reservoir Filling Forecast")
st.write("Forecast Filling Ratio from the latest available observation.")

df_mag = load_data()
area_types = sorted(df_mag["Area Type"].dropna().unique().tolist())
if not area_types:
    st.warning("No area data is available.")
    st.stop()

default_area_type = "EL" if "EL" in area_types else area_types[0]

with st.expander("Parameter Settings", expanded=True):
    area_type = st.selectbox(
        "Area Type",
        options=area_types,
        index=area_types.index(default_area_type),
    )
    area_numbers = sorted(
        df_mag.loc[df_mag["Area Type"] == area_type, "Area Number"]
        .dropna()
        .unique()
        .tolist()
    )
    if not area_numbers:
        st.warning(f"No area numbers are available for area type {area_type}.")
        st.stop()
    default_area_number = 3 if 3 in area_numbers else area_numbers[0]
    area_number = st.selectbox(
        "Area Number",
        options=area_numbers,
        index=area_numbers.index(default_area_number),
    )

    area_data = df_mag.loc[
        (df_mag["Area Type"] == area_type)
        & (df_mag["Area Number"] == area_number),
        ["Date", "Filling Ratio"],
    ].dropna().copy()
    area_data["Date"] = pd.to_datetime(area_data["Date"])
    area_data = area_data.sort_values("Date")
    available_dates = area_data["Date"].drop_duplicates().tolist()

    if not available_dates:
        st.warning(f"No Filling Ratio data is available for {area_type} area {area_number}.")
        st.stop()

    train_start, train_end = st.select_slider(
        "Training date range",
        options=available_dates,
        value=(available_dates[0], available_dates[-1]),
        format_func=lambda date: date.strftime("%Y-%m-%d"),
    )
    horizon = st.slider("Horizon (weeks)", min_value=1, max_value=12, value=12)
    resolution_option = st.select_slider(
        "Resolution",
        options=["1", "2", "M"],
        value="1",
        format_func=lambda option: {
            "1": "1 week",
            "2": "2 weeks",
            "M": "Monthly",
        }[option],
    )
    resolution = int(resolution_option) if resolution_option != "M" else "M"
    st.selectbox(
        "Model",
        options=["Model selection coming soon"],
        disabled=True,
    )

try:
    forecast = forecast_filling(
        df=df_mag,
        area_type=area_type,
        area_number=area_number,
        horizon=horizon,
        train_start=train_start,
        train_end=train_end,
        resolution=resolution,
    )
except ValueError as error:
    st.warning(str(error))
    st.stop()

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=area_data["Date"],
        y=area_data["Filling Ratio"],
        mode="lines",
        name="Historical",
    )
)
fig.add_trace(
    go.Scatter(
        x=forecast["Date"],
        y=forecast["Forecast"],
        mode="lines+markers",
        name="Forecast",
    )
)
fig.update_layout(
    title=f"Filling Ratio Forecast - {area_type} area {area_number}",
    xaxis_title="Date",
    yaxis_title="Filling Ratio",
    template="plotly_white",
)
st.plotly_chart(fig, width="stretch")

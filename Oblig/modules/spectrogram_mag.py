import numpy as np
import pandas as pd
import streamlit as st
from scipy.signal import spectrogram


# Defining spectrogram function with parameters as requested.
def plot_spectrogram(
    df_mag,
    area_type="EL",
    area_number=3,
    window_length=52,
    window_overlap=26,):

    # Selecting data by area type and number function parameters.
    data = df_mag.loc[
        (df_mag["Area Type"] == area_type)
        & (df_mag["Area Number"] == area_number),
        ["Date", "Filling Ratio"],
    ].dropna(subset=["Date", "Filling Ratio"]).copy()

    # Creating pd datetime objects for plotting.
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")

    # Defining errors to be raised in potentially common cases.
    if data.empty:
        raise ValueError(f"No data found for {area_type} area {area_number}.")
    if window_length < 2 or not 0 <= window_overlap < window_length:
        raise ValueError("window_length must be at least 2 and window_overlap must be smaller.")
    if len(data) < window_length:
        raise ValueError("There are fewer observations than the window length.")

    # Creating spectrogram using spectrogram() function.
    frequencies, times, power = spectrogram(
        data["Filling Ratio"].to_numpy(),
        fs=52,
        nperseg=window_length,
        noverlap=window_overlap,)

    # Converting power to decibels for easier plotting.
    power_db = 10 * np.log10(np.maximum(power, np.finfo(float).tiny))

    # Plotting.
    spectrogram_data = pd.DataFrame(
        {
            "Time": np.tile(times, len(frequencies)),
            "Frequency": np.repeat(frequencies, len(times)),
            "Power (dB)": power_db.ravel(),
        }
    )

    st.subheader(f"Spectrogram of Filling Ratio - {area_type} area {area_number}")
    st.vega_lite_chart(
        spectrogram_data,
        {
            "mark": {"type": "rect"},
            "encoding": {
                "x": {
                    "field": "Time",
                    "type": "ordinal",
                    "sort": "ascending",
                    "axis": {"title": "Time (years from start)"},
                },
                "y": {
                    "field": "Frequency",
                    "type": "ordinal",
                    "sort": "ascending",
                    "axis": {"title": "Frequency (cycles per year)"},
                },
                "color": {
                    "field": "Power (dB)",
                    "type": "quantitative",
                    "legend": {"title": "Power (dB)"},
                },
            },
        },
        use_container_width=True,
    )

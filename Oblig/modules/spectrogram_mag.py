import numpy as np
import pandas as pd
import plotly.graph_objects as go
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

    # Plotting with a shared color scale so area changes are comparable.
    fig = go.Figure(
        go.Heatmap(
            x=times,
            y=frequencies,
            z=power_db,
            zmin=-130,
            zmax=-10,
            colorscale="Viridis",
            colorbar={"title": "Power (dB)"},
        )
    )
    fig.update_layout(
        title=f"Spectrogram of Filling Ratio - {area_type} area {area_number}",
        xaxis_title="Time (years from start)",
        yaxis_title="Frequency (cycles per year)",
        template="plotly_white",
    )
    st.plotly_chart(
        fig,
        width="stretch",
        key=(
            f"spectrogram-{area_type}-{area_number}-"
            f"{data['Date'].min().strftime('%Y%m%d')}-"
            f"{data['Date'].max().strftime('%Y%m%d')}"
        ),
    )

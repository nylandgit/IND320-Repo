from modules.api_mag import load_data
import streamlit as st
from modules.stl_mag import plot_stl_decomposition
from modules.spectrogram_mag import plot_spectrogram

# Creating page title and csv load information.
st.title("Seasonal-Trend Decomposition using LOESS and Spectrogram")

df = load_data()
area_type = st.session_state["global_area_type"]
area_number = st.session_state["global_area_number"]
year_start, year_end = st.session_state["global_year_range"]
month_start, month_end = st.session_state["global_month_range"]

selected_data = df[
    (df["Area Type"] == area_type)
    & (df["Area Number"] == area_number)
    & (df["Date"].dt.year >= year_start)
    & (df["Date"].dt.year <= year_end)
    & (df["Date"].dt.month >= month_start)
    & (df["Date"].dt.month <= month_end)
].copy()

# Splitting page into left and right columns.
left_tab, right_tab = st.tabs(["STL Analysis", "Spectrogram"])

# --- Left Tab

with left_tab:
    filling_ratio = selected_data["Filling Ratio"].dropna()
    if filling_ratio.shape[0] < 104:
        st.warning("Select at least 104 weekly observations for STL analysis.")
    else:
        plot_stl_decomposition(
            selected_data,
            area_type,
            area_number,
            "Filling Ratio",
        )


# --- Right Tab

with right_tab:
    if selected_data["Filling Ratio"].dropna().shape[0] < 52:
        st.warning("Select at least 52 weekly observations for the spectrogram.")
    else:
        plot_spectrogram(
            selected_data,
            area_type,
            area_number,
        )

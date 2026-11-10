#from Oblig.modules.api_mag import load_data
#import pandas as pd
import streamlit as st
from modules.stl_mag import plot_stl_decomposition
from modules.spectrogram_mag import plot_spectrogram

# Loading csv into df.
#df = load_data()

# Creating page title and csv load information.
st.title("WIP Seasonal-Trend Decomposition using LOESS and Spectrogram")

# Splitting page into left and right columns.
left_column, right_column = st.columns(2)

# --- Left Column

with left_column:

    # Raising error if data not selected on Data Plots page.
    if "selected_data" not in st.session_state:
        st.info("Select data on the Data Plots page first.")
    else:

        # Proceeding if data is selected on Data Plots page.
        selected_data = st.session_state["selected_data"]
        selected_column = st.session_state["selected_column"]

        # Possible check for later, might delete.
        if selected_data[selected_column].dropna().shape[0] < 1:
            st.warning("Select at least 104 weekly observations for STL analysis.")
        else:
            
            # Plotting.
            plot_stl_decomposition(
                selected_data,
                st.session_state["plot_area_type"],
                st.session_state["plot_area_number"],
                selected_column,
            )


# --- Right Column

with right_column:

    if "selected_data" not in st.session_state:
        st.info("Select data on the Data Plots page first.")
    else:
        selected_data = st.session_state["selected_data"]

        if selected_data.dropna(
            subset=["Date", "Filling Ratio"]
        ).shape[0] < 52:
            st.warning("Select at least 52 weekly observations for the spectrogram.")
        else:
            plot_spectrogram(
                selected_data,
                st.session_state["plot_area_type"],
                st.session_state["plot_area_number"],
            )

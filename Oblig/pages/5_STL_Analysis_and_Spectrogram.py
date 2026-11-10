#from Oblig.modules.api_mag import load_data
#import pandas as pd
import streamlit as st
from modules.stl_mag import plot_stl_decomposition

# Loading csv into df.
#df = load_data()

# Creating page title and csv load information.
st.title("WIP Seasonal-Trend Decomposition using LOESS and Spectrogram")
#st.write(f"Select data type and range to plot.")


# Splitting page into left and right columns.
left_column, right_column = st.columns(2)

# --- Left Column

with left_column:

    st.write("STL Analysis")

    if "selected_data" not in st.session_state:
        st.info("Select data on the Data Plots page first.")
    else:
        selected_data = st.session_state["selected_data"]
        selected_column = st.session_state["selected_column"]

        if selected_data[selected_column].dropna().shape[0] < 1:
            st.warning("Select at least 104 weekly observations for STL analysis.")
        else:
            plot_stl_decomposition(
                selected_data,
                st.session_state["plot_area_type"],
                st.session_state["plot_area_number"],
                selected_column,
            )


# --- Right Column

with right_column:
    
    st.write("Spectrogram")

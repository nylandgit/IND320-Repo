from Oblig.modules.api_mag import load_data
import pandas as pd
import streamlit as st

# Loading csv into df.
df = load_data()

# Creating page title and csv load information.
st.title("WIP Seasonal-Trend Decomposition using LOESS and Spectrogram")
#st.write(f"Select data type and range to plot.")


# Splitting page into left and right columns.
left_column, right_column = st.columns(2)

# --- Left Column

with left_column:

    st.write("SPC Analysis")



# --- Right Column

with right_column:
    
    st.write("LOF Analysis")


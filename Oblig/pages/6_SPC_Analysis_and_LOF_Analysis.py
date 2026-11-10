import pandas as pd
import streamlit as st
from modules.precip_function import precipitation_function
from modules.temp_function import temp_function

st.title("SPC Analysis and LOF Anomaly Detection")

# Splitting page into columns as instructed.
left_column, right_column = st.columns(2)

required_keys = (
    "plot_area_type",
    "plot_area_number",
    "selected_start_month",
    "selected_end_month",
)
if not all(key in st.session_state for key in required_keys):
    st.info("Select an area and date range on the Data Plots page first.")
    st.stop()

if st.session_state["plot_area_type"] != "EL":
    st.info("Meteorological analysis is available for EL areas only.")
    st.stop()

region = f"NO {st.session_state['plot_area_number']}"
start_date = (
    pd.Period(st.session_state["selected_start_month"], freq="M")
    .start_time.strftime("%Y-%m-%d")
)
end_date = (
    pd.Period(st.session_state["selected_end_month"], freq="M")
    .end_time.date().isoformat()
)
selection = (region, start_date, end_date)

if st.session_state.get("meteorological_selection") != selection:
    st.info("Initiate retrieval for the selected area and date range first.")
    st.stop()

weather_data = st.session_state["meteorological_data"]



# --- Left Column

with left_column:
    st.subheader("Temperature SPC Analysis")
    fig, _, outlier_summary = temp_function(
        weather_data,
        region=region,
    )
    st.pyplot(fig)
    st.write(outlier_summary)



# --- Right Column

with right_column:
    st.subheader("Precipitation LOF Analysis")
    fig, _, outlier_summary = precipitation_function(
        weather_data,
        region=region,
    )
    st.pyplot(fig)
    st.write(outlier_summary)
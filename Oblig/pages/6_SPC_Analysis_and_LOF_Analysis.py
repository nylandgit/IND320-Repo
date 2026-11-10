import streamlit as st
from modules.precip_function import precipitation_function
from modules.temp_function import temp_function

st.title("SPC Analysis and LOF Anomaly Detection")

if (
    "meteorological_data" not in st.session_state
    or "meteorological_selection" not in st.session_state
):
    st.info("Initiate data retrieval on the Meteorological Data page first.")
    st.stop()

weather_data = st.session_state["meteorological_data"]
region, start_date, end_date = st.session_state["meteorological_selection"]
st.caption(f"Showing {region}, {start_date} to {end_date}")

# Splitting page into columns as instructed.
left_column, right_column = st.columns(2)



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

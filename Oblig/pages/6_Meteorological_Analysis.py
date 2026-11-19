import streamlit as st
from modules.precip_function import precip_function
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
left_tab, right_tab = st.tabs(["Precipitation SPC", "Temperature LOF"])



# --- Left Column

with left_tab:
    st.subheader("Precipitation SPC Analysis")
    with st.expander("Analysis settings"):
        cutoff_input = st.slider(
            "Cutoff period (days)",
            min_value=7,
            max_value=91,
            value=30,
            step=1,
        )
        stdev_n = st.slider(
            "Standard deviations",
            min_value=1.0,
            max_value=4.0,
            value=3.0,
            step=0.25,
            format="%.2f",
        )
    fig, _, outlier_summary = precip_function(
        weather_data,
        region=region,
        cutoff_input=cutoff_input,
        stdev_n=stdev_n,
    )
    st.pyplot(fig)
    st.write(outlier_summary)



# --- Right Column

with right_tab:
    st.subheader("Temperature LOF Analysis")
    with st.expander("Analysis settings"):
        outlier_proportion = st.slider(
            "Outlier proportion",
            min_value=0.001,
            max_value=0.100,
            value=0.010,
            step=0.001,
            format="%.3f",
        )
    fig, _, outlier_summary = temp_function(
        weather_data,
        region=region,
        outlier_proportion=outlier_proportion,
    )
    st.pyplot(fig)
    st.write(outlier_summary)

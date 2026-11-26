import streamlit as st
from modules.satv_function import SATV_function
from modules.lof_function import lof_function

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
left_tab, right_tab = st.tabs(["SATV Analysis", "LOF Analysis"])



# --- Left Column

with left_tab:
    st.subheader("SATV Analysis")
    with st.expander("Analysis settings"):
        weather_property = st.selectbox(
            "Weather property",
            options=["temperature", "precipitation"],
            index=0,
            key="satv_weather_property",
        )
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
    fig, _, outlier_summary = SATV_function(
        weather_data,
        weather_property=weather_property,
        region=region,
        cutoff_input=cutoff_input,
        stdev_n=stdev_n,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write(outlier_summary)



# --- Right Column

with right_tab:
    st.subheader("LOF Analysis")
    with st.expander("Analysis settings"):
        weather_property = st.selectbox(
            "Weather property",
            options=["temperature", "precipitation"],
            index=0,
            key="lof_weather_property",
        )
        outlier_proportion = st.slider(
            "Outlier proportion",
            min_value=0.001,
            max_value=0.100,
            value=0.010,
            step=0.001,
            format="%.3f",
        )
    fig, _, outlier_summary = lof_function(
        weather_data,
        region=region,
        outlier_proportion=outlier_proportion,
        weather_property=weather_property,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write(outlier_summary)

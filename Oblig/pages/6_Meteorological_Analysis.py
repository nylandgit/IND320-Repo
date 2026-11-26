import streamlit as st
from modules.satv_function import SATV_function
from modules.lof_function import lof_function

st.title("SPC Analysis and LOF Anomaly Detection")

SATV_DEFAULTS = {
    "satv_cutoff_input": 30,
    "satv_stdev_n": 3.0,
}
LOF_DEFAULTS = {
    "lof_outlier_proportion": 0.010,
}

def reset_satv_defaults():
    st.session_state.update(SATV_DEFAULTS)

def reset_lof_defaults():
    st.session_state.update(LOF_DEFAULTS)


if (
    "meteorological_data" not in st.session_state
    or "meteorological_selection" not in st.session_state
):
    st.info("Initiate data retrieval on the Meteorological Data page first.")
    st.stop()

weather_data = st.session_state["meteorological_data"]
region, start_date, end_date = st.session_state["meteorological_selection"]
st.caption(f"Showing {region}, {start_date} to {end_date}")

for key, value in SATV_DEFAULTS.items():
    st.session_state.setdefault(key, value)
for key, value in LOF_DEFAULTS.items():
    st.session_state.setdefault(key, value)

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
        st.button(
            "Default",
            key="satv_default_button",
            on_click=reset_satv_defaults,
        )
        cutoff_input = st.slider(
            "Cutoff period (days)",
            min_value=7,
            max_value=91,
            step=1,
            key="satv_cutoff_input",
        )
        stdev_n = st.slider(
            "Standard deviations",
            min_value=1.0,
            max_value=4.0,
            step=0.25,
            format="%.2f",
            key="satv_stdev_n",
        )
    fig, _, outlier_summary = SATV_function(
        weather_data,
        weather_property=weather_property,
        region=region,
        cutoff_input=cutoff_input,
        stdev_n=stdev_n,
    )
    st.plotly_chart(fig, width="stretch")
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
        st.button(
            "Default",
            key="lof_default_button",
            on_click=reset_lof_defaults,
        )
        outlier_proportion = st.slider(
            "Outlier proportion",
            min_value=0.001,
            max_value=0.100,
            step=0.001,
            format="%.3f",
            key="lof_outlier_proportion",
        )
    fig, _, outlier_summary = lof_function(
        weather_data,
        region=region,
        outlier_proportion=outlier_proportion,
        weather_property=weather_property,
    )
    st.plotly_chart(fig, width="stretch")
    st.write(outlier_summary)

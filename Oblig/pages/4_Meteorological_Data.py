import pandas as pd
import streamlit as st
from modules.api_open_meteo import download_region
from modules.sampling_areas_el import sample_areas_el

st.title("WIP Meteorological Data")
st.write(
    """
    Text explaining data selection from Data Plots.
    """)

# Defining required user input for data retrieval to happen.
required_keys = (
    "plot_area_type",
    "plot_area_number",
    "selected_start_month",
    "selected_end_month",
)

# Defining behaviour if not all required user input is present.
if not all(key in st.session_state for key in required_keys):
    st.info("Select an area and date range on the Data Plots page first.")
    st.stop()

# Temporary limitation of program, will fix later.
if st.session_state["plot_area_type"] != "EL":
    st.info("Meteorological data is available for EL areas only.")
    st.stop()

# Retrieving user input.
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

# Creating button.
if st.button("Initiate data retrieval"):
    with st.status("Retrieving meteorological data...", expanded=True) as status:
        locations_by_region_el = sample_areas_el(
            progress_callback=status.write
        )
        weather_data = download_region(
            region,
            start_date,
            end_date,
            locations_by_region_el,
            progress_callback=status.write,
        )

        st.session_state["meteorological_data"] = weather_data
        st.session_state["meteorological_selection"] = selection

        status.update(
            label="Data processing and retrieval complete.",
            state="complete",
            expanded=False,
        )

# Printing progress messages.
if st.session_state.get("meteorological_selection") == selection:
    st.success(
        "Data processing and retrieval complete. "
        "Proceed to the meteorological analysis pages."
    )
elif "meteorological_data" in st.session_state:
    st.info(
        "Stored data is for a different area or date range. "
        "Initiate retrieval again for this selection."
    )

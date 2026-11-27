import streamlit as st
from modules.api_open_meteo import download_region
from modules.sampling_areas_el import sample_areas_el

st.title("Meteorological Data Retrieval")
st.write(
    """
    Downloads meteorological data for the area and year range selected in
    the Global User Input block.
    """)

# Read the shared inputs rendered in the app's Global User Input block.
required_keys = (
    "global_area_type",
    "global_area_number",
    "global_year_range",
)

if not all(key in st.session_state for key in required_keys):
    st.info("Select an area and year range in the Global User Input block first.")
    st.stop()

# Meteorological data is currently available for EL areas only.
area_type = st.session_state["global_area_type"]
area_number = st.session_state["global_area_number"]
start_year, end_year = st.session_state["global_year_range"]
if area_type != "EL":
    st.info("Meteorological data is available for EL areas only.")
    st.stop()

region = f"NO {area_number}"
start_date = f"{start_year}-01-01"
end_date = f"{end_year}-12-31"
include_elevation = st.checkbox(
    "Include Elevation (slower runtime, more accurate data)",
    value=False,
)
selection = (region, start_date, end_date, include_elevation)
global_selection = (area_type, area_number, start_year, end_year)
period_too_long = end_year - start_year + 1 > 2
if period_too_long:
    st.warning(
        "Weather data downloads are limited to a maximum of two years "
        "due to API restrictions."
        "Adjust the year range in the Global User Input block."
    )

if st.button("Initiate data retrieval", disabled=period_too_long):
    with st.status("Retrieving meteorological data...", expanded=True) as status:
        locations_by_region_el = sample_areas_el(n=500)
        weather_data = download_region(
            region=region,
            start_date=start_date,
            end_date=end_date,
            locations_by_region_el=locations_by_region_el,
            progress_callback=status.write,
            include_elevation=include_elevation,
        )

        st.session_state["meteorological_data"] = weather_data
        st.session_state["meteorological_selection"] = selection
        st.session_state["meteorological_global_selection"] = global_selection

        status.update(
            label="Data processing and retrieval complete.",
            state="complete",
            expanded=False,
        )

if st.session_state.get("meteorological_global_selection") == global_selection:
    st.success(
        "Data processing and retrieval complete. "
        "Proceed to the meteorological analysis pages."
    )
elif "meteorological_global_selection" in st.session_state:
    (
        downloaded_area_type,
        downloaded_area_number,
        downloaded_start_year,
        downloaded_end_year,
    ) = st.session_state["meteorological_global_selection"]
    st.info(
        "Stored data is for a different area or year range. "
        f"Downloaded weather data for {downloaded_area_type} "
        f"{downloaded_area_number} {downloaded_start_year}-"
        f"{downloaded_end_year}."
    )

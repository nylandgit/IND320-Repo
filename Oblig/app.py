import runpy
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="IND320 Energy Data Explorer",
    page_icon="⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { visibility: hidden; }
    [data-testid="stAppViewBlockContainer"] {
        max-width: 100%;
        padding-top: 0 !important;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    [data-testid="column"]:first-child {
        max-width: 330px;
    }
    .st-key-page-selector button {
        border-radius: 12px;
        min-height: 52px;
        font-weight: 600;
    }
    [data-testid="stPopoverBody"] {
        width: min(340px, 70vw);
        max-height: calc(100vh - 130px);
        overflow-y: auto;
        z-index: 1000;
        translate: min(300px, 25vw) -80px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def home():
    st.title("IND320 Energy Data Explorer")
    st.caption(
        "Technical details and project information are available in the "
        "[GitHub README](https://github.com/nylandgit/IND320-Repo)."
    )
    st.write(
        "Explore Norwegian reservoir statistics, cross-border electricity flows, "
        "meteorological data, and time-series analysis."
    )
    st.subheader("Quick start")
    st.markdown(
        """
        1. Open **Magasinstatistikk Data Plots**.
        2. Choose the global area type, area number, year range, and month range.
        3. Open **Meteorological Data Retrieval** and retrieve data for the selected range.
        4. Explore **STL Analysis and Spectrogram** and **Meteorological Analysis**.
        """
    )


PAGES = [
    ("Home", "home", None),
    ("Map", "map", "pages/7_Map.py"),
    ("separator", None, None),
    ("Magasinstatistikk Data Plots", "data", "pages/2_Magasinstatistikk_Data_Selector_and_Plots.py"),
    ("Forecast", "forecast", "pages/8_Forecast.py"),
    ("STL Analysis and Spectrogram", "stl", "pages/5_STL_Analysis_and_Spectrogram.py"),
    ("In-Out Flows Chart", "flows", "pages/3_In-Out_Flows_Charts.py"),
    ("separator", None, None),
    ("Meteorological Data Retrieval", "weather_data", "pages/4_Meteorological_Data_Retrieval.py"),
    ("Meteorological Analysis", "meteorological", "pages/6_Meteorological_Analysis.py"),
    ("Correlation Analysis", "correlation", "pages/9_Correlation_Analysis.py"),
]

if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "home"


def select_page(page_key):
    st.session_state["selected_page"] = page_key


# Initialize global inputs once. Widget keys preserve values across page flips.
if "global_area_type" not in st.session_state:
    st.session_state["global_area_type"] = "EL"
if "global_area_number" not in st.session_state:
    st.session_state["global_area_number"] = 3
if "global_year_range" not in st.session_state:
    st.session_state["global_year_range"] = (2020, 2025)
if "global_month_range" not in st.session_state:
    st.session_state["global_month_range"] = (1, 12)

if (
    st.session_state["selected_page"] == "map"
    and st.session_state.get("map_area_type", "Price Areas (EL)") == "Price Areas (EL)"
):
    map_state = st.session_state.get("map_EL") or {}
    points = map_state.get("selection", {}).get("points", [])
    selected_map_area = points[0]["location"] if points else None
    previous_map_area = st.session_state.setdefault(
        "_last_map_el_selection", selected_map_area
    )
    if selected_map_area and selected_map_area != previous_map_area:
        area_number = int(selected_map_area[-1])
        st.session_state["global_area_type"] = "EL"
        st.session_state["global_area_number"] = area_number
    st.session_state["_last_map_el_selection"] = selected_map_area

left, right = st.columns([1, 4], gap="medium")

with left:
    with st.container(key="page-selector"):
        with st.popover(
            "Page Selector",
            icon=":material/menu:",
            use_container_width=True,
            key="page-menu",
        ):
            st.markdown("### Pages")
            for label, page_key, path in PAGES:
                if label == "separator":
                    st.markdown("---")
                    continue
                st.button(
                    label,
                    key=f"nav_{page_key}",
                    use_container_width=True,
                    type="primary" if st.session_state["selected_page"] == page_key else "secondary",
                    on_click=select_page,
                    args=(page_key,),
                )

    with st.container(border=True):
        st.markdown("### Global User Input")
        area_type_column, area_number_column = st.columns(2)
        with area_type_column:
            area_type = st.radio(
                "Select area type",
                options=["EL", "NO", "VASS"],
                key="global_area_type",
            )
        area_options = (
            list(range(1, 6))
            if area_type == "EL"
            else ([0] if area_type == "NO" else list(range(1, 4)))
        )
        with area_number_column:
            current_area_number = st.session_state["global_area_number"]
            if current_area_number not in area_options:
                current_area_number = 3 if area_type == "EL" else area_options[0]
                st.session_state["global_area_number"] = current_area_number
            st.selectbox(
                "Area number",
                options=area_options,
                key="global_area_number",
            )

        st.slider(
            "Select year range",
            min_value=1995,
            max_value=2026,
            key="global_year_range",
        )
        month_start, month_end = st.slider(
            "Select month range",
            min_value=1,
            max_value=12,
            key="global_month_range",
        )
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        st.caption(f"{month_names[month_start - 1]} - {month_names[month_end - 1]}")

        downloaded_selection = st.session_state.get(
            "meteorological_global_selection"
        )
        if downloaded_selection:
            (
                downloaded_area_type,
                downloaded_area_number,
                downloaded_start_year,
                downloaded_end_year,
            ) = downloaded_selection
            current_selection = (
                area_type,
                st.session_state["global_area_number"],
                *st.session_state["global_year_range"],
            )
            if downloaded_selection == current_selection:
                st.success("✓ Selected area and years match downloaded weather data.")
            else:
                st.warning(
                    "✗ Selected inputs do not match downloaded weather data. "
                    f"Downloaded weather data for {downloaded_area_type} "
                    f"{downloaded_area_number} {downloaded_start_year}-"
                    f"{downloaded_end_year}."
                )
        else:
            st.caption("Weather data has not been downloaded yet.")

        # Downstream pages use these aliases for compatibility.
        st.session_state["plot_area_type"] = area_type
        st.session_state["plot_area_number"] = st.session_state["global_area_number"]
        st.session_state["selected_start_year"] = st.session_state["global_year_range"][0]
        st.session_state["selected_end_year"] = st.session_state["global_year_range"][1]
        st.session_state["selected_start_month"] = f"{st.session_state['global_year_range'][0]}-{month_start:02d}"
        st.session_state["selected_end_month"] = f"{st.session_state['global_year_range'][1]}-{month_end:02d}"

with right:
    selected_page = st.session_state["selected_page"]
    if selected_page == "home":
        home()
    else:
        page_path = next(
            path for title, page_key, path in PAGES
            if page_key == selected_page
        )
        runpy.run_path(Path(__file__).resolve().parent / page_path)

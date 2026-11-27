from modules.api_mag import load_data
import pandas as pd
import streamlit as st

# Loading csv into df.
df = load_data()

# Creating page title and csv load information.
st.title("Data Plots")
st.write(f"Select data type and range to plot.")



# --- Plotting Setup ---

# Selecting csv columns to include in chart. Plotting ISO weeks/years
# is considered unnecessary.
columns_to_plot = [
    "Filling Ratio",
    "Filling TWh",
    "FR Last Week",
    "Change FR",
]

# Using the persisted global area selection.
plot_area_type = st.session_state["global_area_type"]
plot_area_number = st.session_state["global_area_number"]

# Selecting data from df matching specified area type and number.
# Plotting all data in chart will lead to overlapping dates, as
# multiple area types and numbers share the same dates.
plot_data = df[
    (df["Area Type"] == plot_area_type)
    & (df["Area Number"] == plot_area_number)
    ][["Date", *columns_to_plot]].set_index("Date")



# --- Selection Slider ---

selected_year_start, selected_year_end = st.session_state["global_year_range"]
selected_month_start, selected_month_end = st.session_state["global_month_range"]
plot_dates = plot_data.index
selected_data = plot_data.loc[
    (plot_dates.year >= selected_year_start)
    & (plot_dates.year <= selected_year_end)
    & (plot_dates.month >= selected_month_start)
    & (plot_dates.month <= selected_month_end)
]
if selected_data.empty:
    start_month = pd.Period(
        f"{selected_year_start}-{selected_month_start:02d}", freq="M"
    )
    end_month = pd.Period(
        f"{selected_year_end}-{selected_month_end:02d}", freq="M"
    )
else:
    start_month = selected_data.index.min().to_period("M")
    end_month = selected_data.index.max().to_period("M")
st.session_state["selected_start_month"] = str(start_month)
st.session_state["selected_end_month"] = str(end_month)



# --- Selection Box ---

# Creating selection box.
selected_column = st.selectbox(
    "Column to plot",
    options=["All columns", *columns_to_plot],
)

# Selecting column(s) to plot based on selection box input, default
# "All columns".
selected_columns = (
    columns_to_plot if selected_column == "All columns" else [selected_column]
)

stl_data = selected_data.reset_index()
stl_data["Area Type"] = plot_area_type
stl_data["Area Number"] = plot_area_number

st.session_state["selected_data"] = stl_data
st.session_state["plot_area_type"] = plot_area_type
st.session_state["plot_area_number"] = plot_area_number
st.session_state["selected_column"] = (
    selected_column if selected_column != "All columns" else "Filling Ratio"
)

if selected_data.empty:
    st.warning("No reservoir observations match the selected global date range.")
    st.stop()

# --- Plotting ---

# Creating plot based on selected colum(s) and data.
st.write(
    f"Showing {plot_area_type} area {plot_area_number} "
    f"from {selected_data.index.min().date()} to {selected_data.index.max().date()}."
)
st.subheader("Reservoir metrics over time")
st.line_chart(
    selected_data,
    y=selected_columns,
    x_label="Date",
    y_label="Metric value",
)

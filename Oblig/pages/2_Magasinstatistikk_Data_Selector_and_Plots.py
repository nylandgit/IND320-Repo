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

# Preparing selectable months from the global year and month ranges.
# * plot_data.index selects the index values (Date) for each column
#   in plot_data. These dates are already sorted chronologically.
# * .to_period("M") converts the dates into monthly periods.
# * .unique() makes the months show up only once in the slider.
# * .tolist() makes available_months a Python list. We now have a de-
#    duplicated, ordered list of available months for our slider.
available_months = plot_data.index.to_period("M").unique().tolist()
selected_year_start, selected_year_end = st.session_state["global_year_range"]
selected_month_start, selected_month_end = st.session_state["global_month_range"]

available_months = [
    month for month in available_months
    if selected_year_start <= month.year <= selected_year_end
    and selected_month_start <= month.month <= selected_month_end
]
if not available_months:
    st.warning("No reservoir observations match the selected global date range.")
    st.stop()

start_month = available_months[0]
end_month = available_months[-1]

# Saving selection to session state for later use on other pages.
st.session_state["selected_start_month"] = str(start_month)
st.session_state["selected_end_month"] = str(end_month)

# Creating pandas object for plotting monthly data in figures. Some
# months in the CSV have more observations than others.
plot_months = plot_data.index.to_period("M")

# Selecting months from plot_months based on selection slider input.
selected_data = plot_data.loc[
    (plot_months >= start_month) & (plot_months <= end_month)
]



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

from modules.db import load_data
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

# Selecting data from specific area type and number.
plot_area_type = "EL"
plot_area_number = 1

# Selecting data from df matching specified area type and number.
# Plotting all data in chart will lead to overlapping dates, as
# multiple area types and numbers share the same dates.
plot_data = df[
    (df["Area Type"] == plot_area_type)
    & (df["Area Number"] == plot_area_number)
][["Date", *columns_to_plot]].set_index("Date")



# --- Selection Slider ---

# Preparing selectable months for selection slider using list:
# * plot_data.index selects the index values (Date) for each column
#   in plot_data. These dates are already sorted chronologically.
# * .to_period("M") converts the dates into monthly periods.
# * .unique() makes the months show up only once in the slider.
# * .tolist() makes available_months a Python list. We now have a de-
#    duplicated, ordered list of available months for our slider.
available_months = plot_data.index.to_period("M").unique().tolist()

# Creating selection slider for selecting specific subsets of months,
# using ready-made available_months list.
start_month, end_month = st.select_slider(
    "Select months",
    options=available_months,
    value=(available_months[0], available_months[0]),
    format_func=str,
)

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

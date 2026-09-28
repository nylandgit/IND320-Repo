import pandas as pd
import streamlit as st
from pathlib import Path

# Defining .csv path relative to data page .py file.
DATA_PATH = Path(__file__).parent.parent / "data" / "reservoirs.csv"

# Instructing Streamlit to cache load data function so the csv isn't
# reloaded with every Streamlit page action.
@st.cache_data
def load_data():
	return pd.read_csv(DATA_PATH)

# Loading csv into df.
df = load_data()

# Translating Norwegian column names into understandable English.
df = df.rename(columns={
    "dato_Id": "Date",
    "omrType": "Area Type",
    "omrnr": "Area Number",
    "iso_aar": "ISO Year",
    "iso_uke": "ISO Week",
    "fyllingsgrad": "Filling Ratio",
    "kapasitet_TWh": "Capacity TWh",
    "fylling_TWh": "Filling TWh",
    "neste_Publiseringsdato": "Next Publishing Date",
    "fyllingsgrad_forrige_uke": "FR Last Week",
    "endring_fyllingsgrad": "Change FR",
})

# Sorting by date, oldest to newest.
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date", ascending=True)

# Creating page title and csv load information.
st.title("Reservoir data")
st.write(f"Loaded {len(df):,} rows from {DATA_PATH.name}.")



""" Plotting """

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


available_months = plot_data.index.to_period("M").unique().tolist()
start_month, end_month = st.select_slider(
    "Select months",
    options=available_months,
    value=(available_months[0], available_months[0]),
    format_func=str,
)
plot_months = plot_data.index.to_period("M")
selected_data = plot_data.loc[
    (plot_months >= start_month) & (plot_months <= end_month)
]

selected_column = st.selectbox(
    "Column to plot",
    options=["All columns", *columns_to_plot],
)
selected_columns = (
    columns_to_plot if selected_column == "All columns" else [selected_column]
)

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


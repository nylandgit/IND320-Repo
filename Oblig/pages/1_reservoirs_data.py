from modules.db import DATA_PATH, load_data
import pandas as pd
import streamlit as st

# Loading csv into df.
df = load_data()

# Creating page title and csv load information.
st.title("Reservoir data")
st.write(f"Loaded {len(df):,} rows from {DATA_PATH.name}.")



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

# Creating chart title and information.
st.write(
    f"Showing {plot_area_type} area {plot_area_number} "
    f"from {plot_data.index.min().date()} to {plot_data.index.max().date()}."
)

# Creating two-column table w/ column titles and LineChartColumn().
chart_table = pd.DataFrame(
    {
        "Data category": columns_to_plot,
        "Flowchart": [plot_data[column].dropna().tolist() for column in columns_to_plot],
    }
)
st.dataframe(
    chart_table,
    column_config={
        "Flowchart": st.column_config.LineChartColumn("Flowchart"),
    },
    hide_index=True,
    use_container_width=True,
)

from modules.api import load_data
import pandas as pd
import streamlit as st

# Loading API into df.
df = load_data()

# Creating page title and API load information.
st.title("Reservoir data")
st.write(f"Loaded {len(df):,} rows.")



# --- Plotting Setup ---

# Selecting df columns to include in chart. Plotting ISO weeks/years
# is considered unnecessary.
columns_to_plot = [
    "Filling Ratio",
    "Filling TWh",
    "FR Last Week",
    "Change FR",
]

# Taking user input to decide which area type is to be plotted.
plot_area_type = st.radio(
    "Select area type",
    options=["EL", "NO", "VASS"],
)

# Selecting data for the chosen area type. Each area number gets its
# own sparkline column so values from different regions are not mixed.
plot_data = df[df["Area Type"] == plot_area_type]
area_numbers = sorted(plot_data["Area Number"].unique())

# Creating chart title and information.
st.write(
    f"Showing {plot_area_type} areas {', '.join(map(str, area_numbers))} "
    f"from {plot_data['Date'].min().date()} to {plot_data['Date'].max().date()}."
)

# Creating one LineChartColumn per area number.
chart_table = pd.DataFrame({"Data category": columns_to_plot})
column_config = {}
for area_number in area_numbers:
    area_data = plot_data[plot_data["Area Number"] == area_number]
    area_column = f"Area {area_number}"
    chart_table[area_column] = [
        area_data[column].dropna().tolist() for column in columns_to_plot
    ]
    column_config[area_column] = st.column_config.LineChartColumn(area_column)

st.dataframe(
    chart_table,
    column_config=column_config,
    hide_index=True,
    use_container_width=True,
)

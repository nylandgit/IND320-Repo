import pandas as pd
import streamlit as st
from pathlib import Path

# Define .csv path relative to data page .py file.
DATA_PATH = Path(__file__).parent.parent / "data" / "reservoirs.csv"

# Instruct Streamlit to cache load data function. (?)
@st.cache_data
def load_data():
	return pd.read_csv(DATA_PATH)

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

# Sort by date, oldest to newest.
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date", ascending=True)

st.title("Reservoir data")
st.write(f"Loaded {len(df):,} rows from {DATA_PATH.name}.")

columns_to_plot = [
    "Filling Ratio",
    "Filling TWh",
    "FR Last Week",
    "Change FR",
]

#st.line_chart(df, x="Date", y=columns_to_plot)


plot_area_type = "EL"
plot_area_number = 1
plot_data = df[
    (df["Area Type"] == plot_area_type)
    & (df["Area Number"] == plot_area_number)
][["Date", *columns_to_plot]].set_index("Date")

st.write(
    f"Showing {plot_area_type} area {plot_area_number} "
    f"from {plot_data.index.min().date()} to {plot_data.index.max().date()}."
)
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

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

# Selecting the first month of data for displaying.
first_month = df["Date"].dt.to_period("M").min()    # dt = datetime
first_month_data = df[df["Date"].dt.to_period("M") == first_month]



# Transforming data table into summary table w/ one row per column.
# This is achieved by creating a list of dictionaries, where each
# dictionary is the first month of a selected df column.
#
# Additional notes:
# LinceChartColumn() needs values stored as Pythin lists, so we use
# .tolist() to convert the output of the ...[column] function, as the
# output is a pandas series.
summary_rows = []
for column in df.columns:
    values = first_month_data[column].tolist()
    summary_rows.append({
        "Column": column,
        "Data type": str(df[column].dtype),
        "First month": values if pd.api.types.is_numeric_dtype(df[column]) else [],
    })

summary_df = pd.DataFrame(summary_rows)



st.write(f"Line charts show values from the first month: {first_month}.")
st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "First month": st.column_config.LineChartColumn(
            "First month",
            width="large",
        ),
    },
)

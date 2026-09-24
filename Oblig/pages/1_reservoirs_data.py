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
st.dataframe(
    df.head(),
    use_container_width=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="DD.MM.YYYY",
        ),
    },
)

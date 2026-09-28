from pathlib import Path
import pandas as pd
import streamlit as st

# Defining .csv path relative to data page .py file.
DATA_PATH = Path(__file__).parent.parent / "data" / "reservoirs.csv"

# Instructing Streamlit to cache load data function so the csv isn't
# reloaded with every Streamlit page action.
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

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
    return df.sort_values("Date", ascending=True)

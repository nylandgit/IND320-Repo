import pandas as pd
import streamlit as st

from pyjstat import pyjstat
import requests

url = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"

# Retrieving data from API with .get().
response = requests.get(url, timeout=30)
response.raise_for_status()


# Instructing Streamlit to cache load data function so the data isn't
# reloaded with every Streamlit page action.
@st.cache_data
def load_data():
    df = pd.read_csv(response)

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

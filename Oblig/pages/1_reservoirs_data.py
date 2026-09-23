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

st.title("Reservoir data")
st.write(f"Loaded {len(df):,} rows from {DATA_PATH.name}.")
st.dataframe(df.head(), use_container_width=True)

import pandas as pd
import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Instructing Streamlit to cache load data function so the csv isn't
# reloaded with every Streamlit page action.
@st.cache_data

# Defining function to load MongoDB data into pandas df.
def load_flow_data() -> pd.DataFrame:
    
    psw = st.secrets["psw"]

    uri = ("mongodb+srv://ipynb_user:"+psw+ "@nylandcluster.zizrxuq.mongodb.net/")

    # Retrieving MongoDB data.
    with MongoClient(uri, server_api=ServerApi("1")) as client:
        collection = client["ENTSO-E_MW_Flow"]["data"]
        documents = list(collection.find({}, {"_id": 0}))

    return pd.DataFrame.from_records(documents)

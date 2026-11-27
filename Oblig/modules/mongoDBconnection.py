import pandas as pd
import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

@st.cache_data
def load_flow_data() -> pd.DataFrame:
    psw = st.secrets["psw"]

    uri = ("mongodb+srv://ipynb_user:"+psw+ "@nylandcluster.zizrxuq.mongodb.net/")

    with MongoClient(uri, server_api=ServerApi("1")) as client:
        collection = client["ENTSO-E_MW_Flow"]["data"]
        documents = list(collection.find({}, {"_id": 0}))

    return pd.DataFrame.from_records(documents)

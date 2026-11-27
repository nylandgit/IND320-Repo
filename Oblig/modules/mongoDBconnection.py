import pandas as pd
import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

@st.cache_data
def load_flow_data(query: dict) -> pd.DataFrame:
    psw = st.secrets["psw"]

    uri = ("mongodb+srv://ipynb_user:"+psw+ "@nylandcluster.zizrxuq.mongodb.net/")

    with MongoClient(uri, server_api=ServerApi("1")) as client:
        collection = client["ENTSO-E_MW_Flow"]["data"]
        documents = list(
            collection.find(
                query,
                {
                    "_id": 0,
                    "timestamp": 1,
                    "flow_mw": 1,
                    "direction": 1,
                    "norway_zone": 1,
                    "neighbor_zone": 1,
                },
            )
        )

    return pd.DataFrame.from_records(
        documents,
        columns=["timestamp", "flow_mw", "direction", "norway_zone", "neighbor_zone"],
    )


@st.cache_data
def load_latest_flow_timestamp(norway_zone: str, neighbor_zone: str):
    psw = st.secrets["psw"]
    uri = ("mongodb+srv://ipynb_user:"+psw+ "@nylandcluster.zizrxuq.mongodb.net/")
    query = {"norway_zone": norway_zone, "neighbor_zone": neighbor_zone}

    with MongoClient(uri, server_api=ServerApi("1")) as client:
        collection = client["ENTSO-E_MW_Flow"]["data"]
        latest_document = collection.find_one(
            query,
            {"_id": 0, "timestamp": 1},
            sort=[("timestamp", -1)],
        )

    if latest_document is None:
        return None
    return pd.to_datetime(latest_document["timestamp"], utc=True)

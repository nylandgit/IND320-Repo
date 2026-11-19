import streamlit as st

def home():
    st.title("Welcome to Placeholder App")
    st.text("""
        Use sidebar menu to browse pages. See GitHub README located at
        https://github.com/nylandgit/IND320-Repo for further information.
    """)

pages = [
    st.Page(home, title="Home"),
    st.Page("pages/1_Reservoirs_Data_(ToBeRemoved).py", title="Reservoirs Data (ToBeRemoved)"),
    st.Page("pages/2_Magasinstatistikk_Data_Selector_and_Plots.py", title="Magasinstatistikk Data Selector and Plots"),
    st.Page("pages/3_In-Out_Flows_Charts.py", title="In-Out Flows Charts"),
    st.Page("pages/4_Meteorological_Data_Retrieval.py", title="Meteorological Data Retrieval"),
    st.Page("pages/5_STL_Analysis_and_Spectrogram.py", title="STL Analysis and Spectrogram"),
    st.Page("pages/6_Meteorological_Analysis.py", title="Meteorological Analysis"),
]

page = st.navigation(pages)
page.run()

st.set_page_config(page_title="Home",)

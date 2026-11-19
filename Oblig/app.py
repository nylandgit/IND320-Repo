import streamlit as st

st.set_page_config(page_title="IND320 Energy Data Explorer", page_icon="⚡")


def home():
    st.title("IND320 Energy Data Explorer")

    st.caption(
            "Technical details and project information are available in the "
            "[GitHub README](https://github.com/nylandgit/IND320-Repo)."
        )
    
    st.write(
        "Explore Norwegian reservoir statistics, cross-border electricity flows, "
        "meteorological data, and time-series analysis."
    )

    st.subheader("Quick start")
    st.markdown(
        """
        1. Open **Magasinstatistikk Data Selector and Plots**.
        2. Choose an **area type**, **area number**, **month range**, and **column**.
        3. Open **Meteorological Data Retrieval** and retrieve data for the selected range.
        4. Explore the analyses in **STL Analysis and Spectrogram** and
           **Meteorological Analysis**.
        """
    )

    st.subheader("Page guide")

    with st.expander("Magasinstatistikk Data Selector and Plots"):
        st.write(
            "WIP."
        )

    with st.expander("In-Out Flows Charts"):
        st.write(
            "WIP."
        )

    with st.expander("Meteorological Data Retrieval"):
        st.write(
            "WIP."
        )

    with st.expander("STL Analysis and Spectrogram"):
        st.write(
            "WIP."
        )

    with st.expander("Meteorological Analysis"):
        st.write(
            "WIP."
        )

    st.subheader("Navigation tip")
    st.info("Use the sidebar to move between pages. Selections are kept while the app is running.")

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

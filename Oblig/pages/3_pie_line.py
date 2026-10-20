import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from modules.mongoDBconnection import load_flow_data

st.title("Pie and Line Charts")

# Calling function from mongoDBconnection.py module.
df = load_flow_data()

# Converting API data columns to pandas datetime and numberic objects.
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df["flow_mw"] = pd.to_numeric(df["flow_mw"])

# Splitting page into left and right columns.
left_column, right_column = st.columns(2)



# --- Left Column ---

with left_column:
    st.subheader("Flow by Norwegian zone")

    # Creating placeholder radio buttons (see log).
    st.radio(
        "Connection (coming soon)",
        options=["Connection A", "Connection B"],
        disabled=True,
        help="Connection filtering will be added later.",)

    years = [2025, 2026]
        
    # Creating selection box to take user input for year.
    selected_year = st.selectbox("Select year", options=years)

    # Selecting data based on user-inputted year.
    year_data = df[df["timestamp"].dt.year == selected_year]
    
    # Selecting zones.
    zones = ["NO_1", "NO_2", "NO_3", "NO_4"]
    zone_totals = (
        year_data.groupby("norway_zone")["flow_mw"]
        .sum()
        .reindex(zones, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        zone_totals,
        labels=zone_totals.index,
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title(f"Flow in and out by Norwegian zone — {selected_year}")
    ax.axis("equal")

    st.pyplot(fig)
    plt.close(fig)

with right_column:
    pass

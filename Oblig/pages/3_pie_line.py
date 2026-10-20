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

    # Plotting.
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



# --- Right Column ---

with right_column:
    st.subheader("Flow between NO_4 and SE_1")

    # Limit the data to the most recent year, then select the connection.
    latest_timestamp = df["timestamp"].max()
    one_year_ago = latest_timestamp - pd.DateOffset(years=1)

    line_data = df[
        (df["timestamp"] >= one_year_ago)
        & (df["norway_zone"] == "NO_4")
        & (df["neighbor_zone"] == "SE_1")
    ].sort_values("timestamp")

    # Create readable month labels, with the latest month first.
    months = (
        line_data["timestamp"]
        .dt.strftime("%b %Y")
        .drop_duplicates()
        .tolist()[::-1]
    )

    selected_months = st.pills(
        "Select months",
        options=months,
        default=months,
        selection_mode="multi",
    )

    if selected_months:
        plot_data = line_data[
            line_data["timestamp"].dt.strftime("%b %Y").isin(selected_months)
        ]

        fig, ax = plt.subplots(figsize=(8, 5))

        for direction, label in [
            ("out", "Out: NO_4 to SE_1"),
            ("in", "In: SE_1 to NO_4"),
        ]:
            direction_data = plot_data[plot_data["direction"] == direction]
            if not direction_data.empty:
                ax.plot(
                    direction_data["timestamp"],
                    direction_data["flow_mw"],
                    label=label,
                )

        ax.set_title("NO_4-SE_1 flow")
        ax.set_xlabel("Date")
        ax.set_ylabel("Flow (MW)")
        ax.legend()
        ax.grid(True)
        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Select one or more months to display the line chart.")


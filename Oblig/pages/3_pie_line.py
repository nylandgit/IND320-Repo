import pandas as pd
import streamlit as st
from modules.mongoDBconnection import load_flow_data

st.title("Pie and Line Charts")

df = load_flow_data()

# Converting API data columns to pandas datetime and numberic objects.
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df["flow_mw"] = pd.to_numeric(df["flow_mw"])

# Splitting page into left and right columns.
left_column, right_column = st.columns(2)

# Creating dictionary of paired zones from ENTSO-E map.
brz_pairings = {
    "NO_1": ["SE_3"],
    "NO_2": ["DK_1", "GB", "DE_LU", "NL"],
    "NO_3": ["SE_2"],
    "NO_4": ["SE_1", "SE_2", "FI", "RU"],
}


# --- LEFT COLUMN ---

with left_column:

    # Pulling connections out of the brz_pairings dictionary.
    connections = [
        f"{norway_zone} ↔ {neighbor_zone}"
        for norway_zone, neighbor_zones in brz_pairings.items()
        for neighbor_zone in neighbor_zones]

    # Creating radio buttons to let user select plotting connection.
    selected_connection = st.radio("Select connection", options=connections)
    zones = selected_connection.split(" ↔ ")
    st.subheader(f"Flow in and out on the {zones[0]}–{zones[1]} connection")

    # Creating selection box to take user input for year.
    selected_year = st.selectbox("Select year", options=[2025, 2026])
    year_data = df[df["timestamp"].dt.year == selected_year]

    # Selecting data based on zones and user-inputted year.
    year_data = year_data[
        (year_data["norway_zone"] == zones[0])
        & (year_data["neighbor_zone"] == zones[1])]
    
    pie_data = (
        year_data.groupby("direction")["flow_mw"]
        .sum()
        .reindex(["in", "out"], fill_value=0)
        .rename_axis("Direction")
        .reset_index(name="Flow (MW)")
        .replace({"Direction": {"in": f"In: {zones[1]} to {zones[0]}", "out": f"Out: {zones[0]} to {zones[1]}"}}))

    # Plotting using built-in Streamlit functions.
    st.vega_lite_chart(
        pie_data,
        {
            "mark": {"type": "arc", "outerRadius": 120},
            "encoding": {
                "theta": {"field": "Flow (MW)", "type": "quantitative"},
                "color": {"field": "Direction", "type": "nominal"},
                "tooltip": [
                    {"field": "Direction", "type": "nominal"},
                    {"field": "Flow (MW)", "type": "quantitative"},
                ],
            },
        },
        use_container_width=True,
    )



# --- RIGHT COLUMN ---

with right_column:
    st.subheader("Flow between NO_4 and SE_1")

    # Defining time period for data (last year).
    latest_timestamp = df["timestamp"].max()
    one_year_ago = latest_timestamp - pd.DateOffset(years=1)

    # Selecting data for plotting based on time period and connection.
    # See log for information.
    line_data = df[
        (df["timestamp"] >= one_year_ago)
        & (df["norway_zone"] == "NO_4")
        & (df["neighbor_zone"] == "SE_1")
    ].sort_values("timestamp")

    # Defining months the user can select.
    if line_data.empty:
        st.info("No data is available for this connection in the most recent year.")
    else:
        months = (
            line_data["timestamp"]
            .dt.strftime("%b %Y")
            .drop_duplicates()
            .tolist()[::-1])

        # Creating pills for selecting months. Default is most recent.
        selected_months = st.pills(
            "Select months",
            options=months,
            default=months[0],
            selection_mode="multi",)

        # Formatting each month as label shown in Streamlit.
        if selected_months:
            plot_data = line_data[
                line_data["timestamp"].dt.strftime("%b %Y").isin(selected_months)]

            # Plotting.
            flow_by_direction = (
                plot_data.pivot_table(
                    index="timestamp",
                    columns="direction",
                    values="flow_mw",
                    aggfunc="sum",
                )
                .rename(
                    columns={
                        "out": "Out: NO_4 to SE_1",
                        "in": "In: SE_1 to NO_4",
                    }
                )
                .sort_index())

            st.line_chart(
                flow_by_direction,
                x_label="Date",
                y_label="Flow (MW)",)
        else:
            st.info("Select one or more months to display the line chart.")



# --- Source information ---

with st.expander("About this data"):
    st.write(
        """
        The charts use ENTSO-E flow data stored in the project's MongoDB Atlas          
        database. The pie chart sums flow by Norwegian zone for the selected
        year. The line chart shows incoming and outgoing flow between NO_4 and
        SE_1 for the selected months in the most recent year of available data.

        This page does not function exactly as the author guesses was Liland's
        intention. The author guesses that page 3 was supposed to plot a pie
        chart and a line chart based on user-inputted time period(s) and
        user-inputted BRZ connections. This functionality is not compatible
        with the current implementation, where the pie chart in both Streamlit
        and the Jupyter Notebook plots cross-national-border in/out flows per
        Norwegian BRZ in relation to each other, and not cross-national
        connections in relation to each other. Because the plots rely on data
        from the ENTSO-E API, and extracting this data has proved cumbersome
        due to the Spark-Python version bug, the author deems a rework
        unfeasable at this stage of the project (looking forward to some
        feedback on this :D ).
        """
        )

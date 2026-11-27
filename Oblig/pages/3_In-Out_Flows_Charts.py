import pandas as pd
import streamlit as st
from modules.mongoDBconnection import load_flow_data, load_latest_flow_timestamp

st.title("In/Out Flows")

# Splitting page into left and right columns.
left_column, right_column = st.columns(2)

# Creating dictionary of paired zones from ENTSO-E map.
brz_pairings = {
    "NO_1": ["SE_3"],
    "NO_2": ["DK_1", "GB", "DE_LU", "NL"],
    "NO_3": ["SE_2"],
    "NO_4": ["SE_1", "SE_2", "FI", "RU"],
}


def update_selected_connection(widget_key, other_widget_key):
    st.session_state["flow_selected_connection"] = st.session_state[widget_key]
    st.session_state[other_widget_key] = None


# --- LEFT COLUMN ---

with left_column:

    # Pulling connections out of the brz_pairings dictionary.
    connections = [
        f"{norway_zone} ↔ {neighbor_zone}"
        for norway_zone, neighbor_zones in brz_pairings.items()
        for neighbor_zone in neighbor_zones]

    st.session_state.setdefault("flow_connection_left", connections[0])
    st.session_state.setdefault("flow_connection_right", None)
    st.session_state.setdefault("flow_selected_connection", connections[0])

    # Split the single connection selection across two columns.
    radio_columns = st.columns(2)
    with radio_columns[0]:
        st.radio(
            "Select connection",
            options=connections[::2],
            key="flow_connection_left",
            on_change=update_selected_connection,
            args=("flow_connection_left", "flow_connection_right"),
        )
    with radio_columns[1]:
        st.radio(
            " ",
            options=connections[1::2],
            key="flow_connection_right",
            on_change=update_selected_connection,
            args=("flow_connection_right", "flow_connection_left"),
            label_visibility="collapsed",
        )

    selected_connection = st.session_state["flow_selected_connection"]
    zones = selected_connection.split(" ↔ ")
    st.subheader(f"Flow in and out on the {zones[0]}–{zones[1]} connection")

    # Creating selection box to take user input for year.
    selected_year = st.selectbox("Select year", options=[2025, 2026])

    # Retrieve only the selected connection and year from MongoDB.
    year_start = pd.Timestamp(year=selected_year, month=1, day=1, tz="UTC")
    next_year_start = pd.Timestamp(year=selected_year + 1, month=1, day=1, tz="UTC")
    year_data = load_flow_data(
        {
            "norway_zone": zones[0],
            "neighbor_zone": zones[1],
            "timestamp": {"$gte": year_start.to_pydatetime(), "$lt": next_year_start.to_pydatetime()},
        }
    )
    year_data["timestamp"] = pd.to_datetime(year_data["timestamp"], utc=True)
    year_data["flow_mw"] = pd.to_numeric(year_data["flow_mw"])
    
    # Average the 15-minute MW readings within each hour before summing to MWh.
    hourly_flow = (
        year_data.pivot_table(
            index="timestamp",
            columns="direction",
            values="flow_mw",
            aggfunc="mean",
        )
        .resample("1h")
        .mean()
        .sum()
    )
    pie_data = (
        hourly_flow
        .reindex(["in", "out"], fill_value=0)
        .rename_axis("Direction")
        .reset_index(name="Flow (MWh)")
        .replace({"Direction": {"in": f"In: {zones[1]} to {zones[0]}", "out": f"Out: {zones[0]} to {zones[1]}"}}))

    # Plotting using built-in Streamlit functions.
    st.vega_lite_chart(
        pie_data,
        {
            "mark": {"type": "arc", "outerRadius": 120},
            "encoding": {
                "theta": {"field": "Flow (MWh)", "type": "quantitative"},
                "color": {
                    "field": "Direction",
                    "type": "nominal",
                    "legend": {"orient": "bottom", "direction": "horizontal"},
                },
                "tooltip": [
                    {"field": "Direction", "type": "nominal"},
                    {"field": "Flow (MWh)", "type": "quantitative"},
                ],
            },
        },
        use_container_width=True,
    )



# --- RIGHT COLUMN ---

with right_column:
    st.subheader(f"Flow between {zones[0]} and {zones[1]}")

    latest_timestamp = load_latest_flow_timestamp(zones[0], zones[1])
    if latest_timestamp is not None:
        one_year_ago = latest_timestamp - pd.DateOffset(years=1)
        line_data = load_flow_data(
            {
                "norway_zone": zones[0],
                "neighbor_zone": zones[1],
                "timestamp": {
                    "$gte": one_year_ago.to_pydatetime(),
                    "$lte": latest_timestamp.to_pydatetime(),
                },
            }
        )
    else:
        line_data = pd.DataFrame()

    if line_data.empty:
        st.info("No data is available for this connection in the most recent year.")
    else:
        line_data["timestamp"] = pd.to_datetime(line_data["timestamp"], utc=True)
        line_data["flow_mw"] = pd.to_numeric(line_data["flow_mw"])
        line_data = line_data.sort_values("timestamp")

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
                        "out": f"Out: {zones[0]} to {zones[1]}",
                        "in": f"In: {zones[1]} to {zones[0]}",
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
        database. The pie chart shows hourly-average flow summed by direction
        for the selected connection and year. The line chart shows incoming
        and outgoing flow for the selected months in the most recent year of
        available data.
        """
        )

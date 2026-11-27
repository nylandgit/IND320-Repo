import pandas as pd
import streamlit as st
from modules.mongoDBconnection import load_flow_data

st.title("In/Out Flows")

df = load_flow_data()
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

    year_data = df[df["timestamp"].dt.year == selected_year]
    year_data = year_data[
        (year_data["norway_zone"] == zones[0])
        & (year_data["neighbor_zone"] == zones[1])]
    
    # Average absolute 15-minute MW readings within each hour before summing to MWh.
    hourly_flow = (
        year_data.assign(
            hour=year_data["timestamp"].dt.floor("h"),
            flow_mw=year_data["flow_mw"].abs(),
        )
        .groupby(["direction", "hour"])["flow_mw"]
        .mean()
        .groupby(level="direction")
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

    months_2025 = (
        pd.date_range("2025-01-01", "2025-12-01", freq="MS")
        .strftime("%b %Y")
        .tolist()
    )
    months_2026 = (
        pd.date_range("2026-01-01", "2026-10-01", freq="MS")
        .strftime("%b %Y")
        .tolist()
    )
    line_start = pd.Timestamp("2025-01-01", tz="UTC")
    line_end = pd.Timestamp("2026-11-01", tz="UTC")
    line_data = df[
        (df["timestamp"] >= line_start)
        & (df["timestamp"] < line_end)
        & (df["norway_zone"] == zones[0])
        & (df["neighbor_zone"] == zones[1])
    ].sort_values("timestamp")

    month_columns = st.columns(2)
    with month_columns[0]:
        selected_2025 = st.pills(
            "2025",
            options=months_2025,
            selection_mode="multi",
        )
    with month_columns[1]:
        selected_2026 = st.pills(
            "2026",
            options=months_2026,
            default=months_2026[-1],
            selection_mode="multi",
        )
    selected_months = (selected_2025 or []) + (selected_2026 or [])

    if line_data.empty:
        st.info("No data is available for this connection during 2025 or 2026.")
    else:
        line_data["timestamp"] = pd.to_datetime(line_data["timestamp"], utc=True)
        line_data["flow_mw"] = pd.to_numeric(line_data["flow_mw"])
        line_data = line_data.sort_values("timestamp")

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

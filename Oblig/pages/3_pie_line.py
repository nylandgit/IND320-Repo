import pandas as pd
import streamlit as st
from modules.mongoDBconnection import load_flow_data

st.title("Pie and Line Charts")

df = load_flow_data()

# Converting API data columns to pandas datetime and numberic objects.
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df["flow_mw"] = pd.to_numeric(df["flow_mw"])

left_column, right_column = st.columns(2)

# Splitting page into left and right columns.
left_column, right_column = st.columns(2)


# --- Left column ---

with left_column:
    st.subheader("Flow by Norwegian zone")

    # Creating placeholder radio buttons (see log).
    st.radio(
        "Connection (coming soon)",
        options=["Connection A", "Connection B"],
        disabled=True,
        help="Connection filtering will be added later.")

    # Creating selection box to take user input for year.
    selected_year = st.selectbox("Select year", options=[2025, 2026])
    year_data = df[df["timestamp"].dt.year == selected_year]

    # Selecting zones as in Jupyter Notebook.
    zones = ["NO_1", "NO_2", "NO_3", "NO_4"]
    
    # Selecting data based on zones and user-inputted year.
    pie_data = (
        year_data.groupby("norway_zone")["flow_mw"]
        .sum()
        .reindex(zones, fill_value=0)
        .rename_axis("Zone")
        .reset_index(name="Flow (MW)"))

    # Plotting using built-in Streamlit functions.
    st.vega_lite_chart(
        pie_data,
        {
            "mark": {"type": "arc", "outerRadius": 120},
            "encoding": {
                "theta": {"field": "Flow (MW)", "type": "quantitative"},
                "color": {"field": "Zone", "type": "nominal"},
                "tooltip": [
                    {"field": "Zone", "type": "nominal"},
                    {"field": "Flow (MW)", "type": "quantitative"},
                ],
            },
        },
        use_container_width=True,
    )


# --- Right column ---

with right_column:
    st.subheader("Flow between NO_4 and SE_1")

    # Keep the most recent year of data for the connection used in the notebook.
    latest_timestamp = df["timestamp"].max()
    one_year_ago = latest_timestamp - pd.DateOffset(years=1)

    line_data = df[
        (df["timestamp"] >= one_year_ago)
        & (df["norway_zone"] == "NO_4")
        & (df["neighbor_zone"] == "SE_1")
    ].sort_values("timestamp")

    if line_data.empty:
        st.info("No data is available for this connection in the most recent year.")
    else:
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
                .sort_index()
            )

            st.line_chart(
                flow_by_direction,
                x_label="Date",
                y_label="Flow (MW)",
            )
        else:
            st.info("Select one or more months to display the line chart.")

# --- Source information ---

with st.expander("About this data"):
    st.write(
        "The charts use ENTSO-E flow data stored in the project's MongoDB Atlas "
        "database. The pie chart sums flow by Norwegian zone for the selected "
        "year. The line chart shows incoming and outgoing flow between NO_4 and "
        "SE_1 for the selected months in the most recent year of available data."
    )

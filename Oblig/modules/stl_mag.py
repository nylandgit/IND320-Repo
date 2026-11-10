import pandas as pd
import streamlit as st
from statsmodels.tsa.seasonal import STL

# Defining function w/ requested parameters and relevant defaults.
def plot_stl_decomposition(
    df_mag,
    area_type="EL",
    area_number=3,
    selected_column="Filling Ratio",
    seasonal=13,
    trend=53,
    robust=False,):

    # Selecting data by area type and number function parameters.
    data = df_mag.loc[
        (df_mag["Area Type"] == area_type)
        & (df_mag["Area Number"] == area_number),
        ["Date", selected_column],
    ].dropna(subset=["Date", selected_column]).copy()

    # Creating pd datetime objects for plotting.
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")

    # Defining error to be raised if no data is found for selected area.
    if data.empty:
        raise ValueError(f"No data found for {area_type} area {area_number}.")

    # Decompiling data using STL LOESS.
    result = STL(
        data[selected_column],
        period=52,  # Period = one year. This could need updating to acccount for leap years.
        seasonal=seasonal,
        trend=trend,
        robust=robust,
    ).fit()

    # Plotting.
    components = pd.DataFrame(
        {
            "Observed": data[selected_column].to_numpy(),
            "Trend": result.trend,
            "Seasonal": result.seasonal,
            "Residual": result.resid,
        },
        index=pd.DatetimeIndex(data["Date"], name="Date"),
    )
    labels = ["Observed", "Trend", "Seasonal", "Residual"]

    st.subheader(
        f"STL decomposition of {selected_column} - "
        f"{area_type} area {area_number}"
    )

    for label in labels:
        st.line_chart(
            components,
            y=label,
            x_label="Date",
            y_label=label,
        )

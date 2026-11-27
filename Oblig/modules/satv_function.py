import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.fft import dct, idct

def SATV_function(
    weather_data,
    region="NO 3",
    cutoff_f=None,
    stdev_n=3,
    cutoff_input=30,
    weather_property="temperature",
):
    weather_columns = {
        "temperature": ("temperature_2m", "temperature", "°C"),
        "precipitation": ("precipitation", "precipitation", "mm/hour"),
    }
    column, property_label, unit = weather_columns[weather_property]
    # Taking the average hourly data across all 1000 sampled points.
    precip_avg = weather_data.groupby("date")[column].mean().sort_index()

    # Defining n = number of observations for avg data.
    precip_avg_np = precip_avg.to_numpy(dtype=float)
    n = len(precip_avg_np)
    if cutoff_f is None:
        cutoff_f = np.arange(n) / (2 * n)

    # Defining cutoff period (24 hours/day) and frequency.
    cutoff_period_hours = 24 * cutoff_input

    # Performing DCT. dct() transforms data values from the time domain
    # to DCT coefficients, which are then set to zero if their frequencies are
    # below the cutoff frequency. This effectively removes fluctuations with
    # periods longer than the cutoff.
    coefficients = dct(precip_avg_np, type=1, norm="ortho")
    coefficients[cutoff_f < 1 / cutoff_period_hours] = 0

    # Creating a pandas Series of the remaining coefficients, after converting
    # these back into the time domain using idct(). Voila! High-pass filtering :D
    high_pass_precip = pd.Series(
        idct(coefficients, type=2, norm="ortho"),
        index=precip_avg.index,
        name="SATV",
    )

    # Assuming normal distribution and defining outlier limit to be +-3 STD as
    # explained by the D2D book.
    satv_median = high_pass_precip.median()
    robust_sigma = 1.4826 * (high_pass_precip - satv_median).abs().median()
    satv_lcl = satv_median - stdev_n * robust_sigma
    satv_ucl = satv_median + stdev_n * robust_sigma

    # Identifying outliers from SATV.
    outliers = (high_pass_precip < satv_lcl) | (high_pass_precip > satv_ucl)

    # Translating outliers back into data.
    baseline = precip_avg - high_pass_precip
    lcl = baseline + satv_lcl
    ucl = baseline + satv_ucl

    # Plotting avg data and its SATV-based control limits.
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=precip_avg.index,
            y=lcl,
            mode="lines",
            line={"color": "#D97706", "dash": "dash", "width": 1.5},
            name="Lower control limit",
            legendrank=2,
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>Lower limit: "
                f"%{{y:.2f}} {unit}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=precip_avg.index,
            y=ucl,
            mode="lines",
            line={"color": "#D97706", "dash": "dash", "width": 1.5},
            fill="tonexty",
            fillcolor="rgba(217, 119, 6, 0.10)",
            name="Upper control limit",
            legendrank=3,
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>Upper limit: "
                f"%{{y:.2f}} {unit}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=precip_avg.index,
            y=precip_avg.values,
            mode="lines",
            line={"color": "#2563EB", "width": 2},
            name=f"Average {property_label}",
            legendrank=1,
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>Average {property_label}: "
                f"%{{y:.2f}} {unit}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=high_pass_precip.index[outliers],
            y=precip_avg.loc[outliers],
            mode="markers",
            marker={
                "color": "#DC2626",
                "size": 8,
                "line": {"color": "white", "width": 1},
            },
            name="SATV outliers",
            legendrank=4,
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>Outlier: "
                f"%{{y:.2f}} {unit}<extra></extra>"
            ),
        )
    )

    period = str(precip_avg.index[0].year)
    if precip_avg.index[0].year != precip_avg.index[-1].year:
        period = f"{precip_avg.index[0].year}-{precip_avg.index[-1].year}"
    fig.update_layout(
        title={
            "text": (
                f"SATV-based Statistical Process Control for "
                f"{region} ({period})"
            ),
            "x": 0,
            "xanchor": "left",
            "font": {"size": 18},
        },
        xaxis_title="Time",
        yaxis_title=f"Average {property_label} ({unit})",
        height=500,
        template="plotly_white",
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        margin={"l": 65, "r": 25, "t": 95, "b": 55},
        font={"family": "Arial, sans-serif", "size": 13, "color": "#374151"},
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E5E7EB",
        showline=True,
        linecolor="#D1D5DB",
        zeroline=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5E7EB",
        showline=True,
        linecolor="#D1D5DB",
        zeroline=False,
    )

    outlier_details = pd.DataFrame(
        {
            f"average_{property_label}": precip_avg[outliers],
            "SATV": high_pass_precip[outliers],
        }
    )
    outlier_summary = outlier_details[f"average_{property_label}"].agg(
        ["count", "mean", "min", "max"]
    )

    return fig, outlier_details, outlier_summary

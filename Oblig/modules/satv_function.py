import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        precip_avg.index,
        precip_avg.values,
        label=f"Average {property_label}",
    )
    ax.plot(
        precip_avg.index,
        lcl,
        color="orange",
        linestyle="--",
        label="Lower control limit",
    )
    ax.plot(
        precip_avg.index,
        ucl,
        color="orange",
        linestyle="--",
        label="Upper control limit",
    )
    ax.scatter(
        high_pass_precip.index[outliers],
        precip_avg.loc[outliers],
        color="crimson",
        label="SATV outliers",
        zorder=3,
    )

    period = str(precip_avg.index[0].year)
    if precip_avg.index[0].year != precip_avg.index[-1].year:
        period = f"{precip_avg.index[0].year}-{precip_avg.index[-1].year}"
    ax.set(
        title=f"SATV-based Statistical Process Control for {region} ({period})",
        xlabel="Time",
        ylabel=f"Average {property_label} ({unit})",
    )
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.fft import dct, idct

def temp_function(weather_data, region="NO 3", cutoff_f=None, stdev_n=3):
    # Taking the average hourly temperature across all 1000 sampled points.
    temp_avg = (
        weather_data.groupby("date")["temperature_2m"].mean().sort_index()
    )

    # Defining n = number of observations for avg temperature.
    temp_avg_np = temp_avg.to_numpy(dtype=float)
    n = len(temp_avg_np)
    if cutoff_f is None:
        cutoff_f = np.arange(n) / (2 * n)

    # Defining cutoff period (24 hours/day * 30 days) and frequency.
    cutoff_period_hours = 24 * 30

    # Performing DCT. dct() transforms temperature values from the time domain
    # to DCT coefficients, which are then set to zero if their frequencies are
    # below the cutoff frequency. This effectively removes fluctuations with
    # periods longer than the cutoff.
    coefficients = dct(temp_avg_np, type=1, norm="ortho")
    coefficients[cutoff_f < 1 / cutoff_period_hours] = 0

    # Creating a pandas Series of the remaining coefficients, after converting
    # these back into the time domain using idct(). Voila! High-pass filtering :D
    high_pass_temp = pd.Series(
        idct(coefficients, type=2, norm="ortho"),
        index=temp_avg.index,
        name="SATV",
    )

    # Assuming normal distribution and defining outlier limit to be +-3 STD as
    # explained by the D2D book.
    satv_median = high_pass_temp.median()
    robust_sigma = 1.4826 * (high_pass_temp - satv_median).abs().median()
    satv_lcl = satv_median - stdev_n * robust_sigma
    satv_ucl = satv_median + stdev_n * robust_sigma

    # Identifying outliers from SATV.
    outliers = (high_pass_temp < satv_lcl) | (high_pass_temp > satv_ucl)

    # Translating outliers back into temperature.
    baseline = temp_avg - high_pass_temp
    lcl = baseline + satv_lcl
    ucl = baseline + satv_ucl

    # Plotting avg temperature and its SATV-based control limits.
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(temp_avg.index, temp_avg.values, label="Average temperature")
    ax.plot(
        temp_avg.index,
        lcl,
        color="orange",
        linestyle="--",
        label="Lower control limit",
    )
    ax.plot(
        temp_avg.index,
        ucl,
        color="orange",
        linestyle="--",
        label="Upper control limit",
    )
    ax.scatter(
        high_pass_temp.index[outliers],
        temp_avg.loc[outliers],
        color="crimson",
        label="SATV outliers",
        zorder=3,
    )

    period = str(temp_avg.index[0].year)
    if temp_avg.index[0].year != temp_avg.index[-1].year:
        period = f"{temp_avg.index[0].year}-{temp_avg.index[-1].year}"
    ax.set(
        title=f"SATV-based Statistical Process Control for {region} ({period})",
        xlabel="Time",
        ylabel="Average temperature (°C)",
    )
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    outlier_details = pd.DataFrame(
        {
            "average_temperature": temp_avg[outliers],
            "SATV": high_pass_temp[outliers],
        }
    )
    outlier_summary = outlier_details["average_temperature"].agg(
        ["count", "mean", "min", "max"]
    )

    return fig, outlier_details, outlier_summary

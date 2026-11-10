import matplotlib.pyplot as plt
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor


def precipitation_function(
    weather_data,
    region="NO 3",
    outlier_proportion=0.01,
):
    precip_avg = (
        weather_data.groupby("date")["precipitation"].mean().sort_index()
    )

    # Transforming precip_avg pd Series to numpy array for use in
    # LocalOutlierFactor().
    lof_data = precip_avg.to_numpy().reshape(-1, 1)

    # Using LocalOutlierFactor() as instructed by D2D book.
    lof = LocalOutlierFactor(contamination=outlier_proportion)
    labels = lof.fit_predict(lof_data)
    anomalies = labels == -1

    # Plotting w/ anomalies, outlier details.
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        precip_avg.index,
        precip_avg.values,
        label="Average precipitation",
    )
    ax.scatter(
        precip_avg.index[anomalies],
        precip_avg[anomalies],
        color="red",
        label="Anomalies",
    )

    period = str(precip_avg.index[0].year)
    if precip_avg.index[0].year != precip_avg.index[-1].year:
        period = f"{precip_avg.index[0].year}-{precip_avg.index[-1].year}"
    ax.set(
        title=f"Average precipitation over {region} ({period})",
        xlabel="Time",
        ylabel="Average precipitation (mm/hour)",
    )
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    outlier_details = pd.DataFrame(
        {"average_precipitation": precip_avg[anomalies]}
    )
    outlier_summary = outlier_details.agg(
        ["count", "mean", "min", "max"]
    )

    return fig, outlier_details, outlier_summary

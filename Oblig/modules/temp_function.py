import matplotlib.pyplot as plt
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor


def temp_function(
    weather_data,
    region="NO 3",
    outlier_proportion=0.01,
):
    temp_avg = (
        weather_data.groupby("date")["temperature_2m"].mean().sort_index()
    )

    # Transforming temp_avg pd Series to numpy array for use in
    # LocalOutlierFactor().
    lof_data = temp_avg.to_numpy().reshape(-1, 1)

    # Using LocalOutlierFactor() as instructed by D2D book.
    lof = LocalOutlierFactor(contamination=outlier_proportion)
    labels = lof.fit_predict(lof_data)
    anomalies = labels == -1

    # Plotting w/ anomalies, outlier details.
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        temp_avg.index,
        temp_avg.values,
        label="Average temperature",
    )
    ax.scatter(
        temp_avg.index[anomalies],
        temp_avg[anomalies],
        color="red",
        label="Anomalies",
    )

    period = str(temp_avg.index[0].year)
    if temp_avg.index[0].year != temp_avg.index[-1].year:
        period = f"{temp_avg.index[0].year}-{temp_avg.index[-1].year}"
    ax.set(
        title=f"Average temperature over {region} ({period})",
        xlabel="Time",
        ylabel="Average temperature (°C)",
    )
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    outlier_details = pd.DataFrame(
        {"average_temperature": temp_avg[anomalies]}
    )
    outlier_summary = outlier_details.agg(
        ["count", "mean", "min", "max"]
    )

    return fig, outlier_details, outlier_summary

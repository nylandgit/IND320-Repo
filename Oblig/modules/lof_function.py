import matplotlib.pyplot as plt
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor


def lof_function(
    weather_data,
    region="NO 3",
    outlier_proportion=0.01,
    weather_property="temperature",
):
    weather_columns = {
        "temperature": ("temperature_2m", "temperature", "°C"),
        "precipitation": ("precipitation", "precipitation", "mm/hour"),
    }
    column, property_label, unit = weather_columns[weather_property]
    temp_avg = weather_data.groupby("date")[column].mean().sort_index()

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
        label=f"Average {property_label}",
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
        title=f"Average {property_label} over {region} ({period})",
        xlabel="Time",
        ylabel=f"Average {property_label} ({unit})",
    )
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    outlier_details = pd.DataFrame(
        {f"average_{property_label}": temp_avg[anomalies]}
    )
    outlier_summary = outlier_details.agg(
        ["count", "mean", "min", "max"]
    )

    return fig, outlier_details, outlier_summary

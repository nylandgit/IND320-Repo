import pandas as pd
import plotly.graph_objects as go
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
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=temp_avg.index,
            y=temp_avg.values,
            mode="lines",
            line={"color": "#2563EB", "width": 2},
            name=f"Average {property_label}",
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>Average {property_label}: "
                f"%{{y:.2f}} {unit}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=temp_avg.index[anomalies],
            y=temp_avg[anomalies],
            mode="markers",
            marker={
                "color": "#DC2626",
                "size": 8,
                "line": {"color": "white", "width": 1},
            },
            name="Anomalies",
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>Anomaly: "
                f"%{{y:.2f}} {unit}<extra></extra>"
            ),
        )
    )

    period = str(temp_avg.index[0].year)
    if temp_avg.index[0].year != temp_avg.index[-1].year:
        period = f"{temp_avg.index[0].year}-{temp_avg.index[-1].year}"
    fig.update_layout(
        title={
            "text": f"Average {property_label} over {region} ({period})",
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
        margin={"l": 65, "r": 25, "t": 85, "b": 55},
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
        {f"average_{property_label}": temp_avg[anomalies]}
    )
    outlier_summary = outlier_details.agg(
        ["count", "mean", "min", "max"]
    )

    return fig, outlier_details, outlier_summary

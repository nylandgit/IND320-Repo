import time
from pathlib import Path
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Defining path for saved data (if it exists).
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "meteorological"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Setting up Open-Meteo API client with cache and retry on error.
cache_session = requests_cache.CachedSession(
    str(DATA_DIR / ".cache"), expire_after=-1
)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Defining function with input parameters as instructed and needed.
def download_region(
    region,
    start_date,
    end_date,
    locations_by_region_el,
    progress_callback=None,
):
    url = "https://archive-api.open-meteo.com/v1/archive"
    region_data = []
    
    locations = locations_by_region_el[region]
    points = pd.DataFrame(locations, columns=["lat", "lon"])

    # Merging sampled points into ERA5 grid cells (0.25 degrees). Each cell is
    # requested once, at the mean position and mean elevation of the sampled
    # points inside it. "weight" is the number of sampled points in the cell.
    # This saves API weighted cost, making the retrieval possible with the
    # API's free plan data limits.
    points["cell_lat"] = (points["lat"] / 0.25).round() * 0.25
    points["cell_lon"] = (points["lon"] / 0.25).round() * 0.25

    # Defining cells to be called at mean of lon/lat and elevation.
    cells = points.groupby(["cell_lat", "cell_lon"]).agg(
        lat=("lat", "mean"),
        lon=("lon", "mean"),
        #elevation=("elevation", "mean"),
        weight=("lat", "size"),
    ).reset_index()

    # Printing progress message.
    if progress_callback is not None:
        progress_callback(
            f"Merged {len(points)} points into {len(cells)} ERA5 cells."
        )

    # Setting up chunk-based API data requesting (lots of data).
    chunk_size = 100
    total_chunks = (len(cells) + chunk_size - 1) // chunk_size

    # Iterating over each chunk.
    for chunk_number, chunk_start in enumerate(
        range(0, len(cells), chunk_size), start=1
    ):
        chunk = cells.iloc[chunk_start:chunk_start + chunk_size]

        # Defining parameters as instructed by Open-Meteo API.
        params = {
            "latitude": chunk["lat"].tolist(),
            "longitude": chunk["lon"].tolist(),
            #"elevation": chunk["elevation"].tolist(),
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ["temperature_2m", "precipitation"],
            "models": "era5",
            "timezone": "Europe/Berlin",
        }

        # Printing progress messages (long code execution times).
        if progress_callback is not None:
            progress_callback(
                f"Attempting chunk {chunk_number}/{total_chunks} "
                f"({len(chunk)} cells) for region {region}..."
            )

        responses = openmeteo.weather_api(url, params=params)

        # Iterating over each ERA5 cell.
        for (_, cell), response in zip(chunk.iterrows(), responses):
            hourly = response.Hourly()

            # Creating dictionary to be populated with data from API.
            hourly_data = {
                # Defining "date" key:value pair(s), this is converted to a df
                # column later. Essentially, this block defines the "date"
                # column in our soon-to-exist df. Methodology is from API.
                "date": pd.date_range(
                    start=pd.to_datetime(
                        hourly.Time(), unit="s", utc=True
                    ),
                    end=pd.to_datetime(
                        hourly.TimeEnd(), unit="s", utc=True
                    ),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ).tz_convert(response.Timezone().decode()),

                # Defining temp. and precip. key:value pairs for soon-to-exist df.
                "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
                "precipitation": hourly.Variables(1).ValuesAsNumpy(),
            }

            # Converting data dictionary to pandas df.
            point_data = pd.DataFrame(data=hourly_data)
            point_data["latitude"] = cell["lat"]
            point_data["longitude"] = cell["lon"]
            #point_data["elevation"] = cell["elevation"]
            point_data["weight"] = int(cell["weight"])
            region_data.append(point_data)

        # Another progress message.
        if progress_callback is not None:
            progress_callback(f"Completed chunk {chunk_number}/{total_chunks}.")

        # Pausing between chunks to stay under the API's per-minute limit.
        time.sleep(5)

    # Saving everything to csv so the API call only needs to be done once.
    region_data = pd.concat(region_data, ignore_index=True)
    
    """
    region_data.to_csv(csv_file, index=False)
        if progress_callback is not None:
            progress_callback(f"Saved {len(region_data)} rows to {csv_file.name}.")
        
    """
    return region_data

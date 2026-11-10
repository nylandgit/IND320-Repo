# The following code has been adapted from Open Meteo's Python coding
# example at https://open-meteo.com/en/docs/historical-forecast-api. It
# saves retrieved data to a locally stored .csv to avoid reruns during
# development.
import os
import time
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from modules.sampling_areas_el import sampling_areas_el

locations_by_region_el = sampling_areas_el

# Setting up Open-Meteo API client with cache and retry on error.
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)



# Defining function with input parameters as instructed.
def download_region(region, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    region_data = []

    # Loading saved csv if it exists, so the API only needs to be called once.
    # The f"{...} line looks for files named using the naming logic seen in
    # the last code block of this function.
    csv_file = f"{region.replace(' ', '_')}_{start_date}_{end_date}.csv"
    if os.path.exists(csv_file):
        print(f"Loading {csv_file} from disk, no API calls needed.", flush=True)
        saved = pd.read_csv(csv_file)

        # Converting to date column data to datetime objects (if they exist).
        saved["date"] = pd.to_datetime(saved["date"], utc=True).dt.tz_convert("Europe/Berlin")
        return saved



    locations = locations_by_region_el[region]

    # Getting the elevation of every sampled point from Open-Meteo's Elevation
    # API (max 100 coordinates per request), see code block below. Iterating
    # over sampled points in batches of 100.
    points = pd.DataFrame(locations, columns=["lat", "lon"])
    elevations = []
    for batch_start in range(0, len(points), 100):
        batch = points.iloc[batch_start:batch_start + 100]
        
        # Printing progress messages as program may for several minutes.
        print(f"Getting elevations for points {batch_start + 1}-"
              f"{batch_start + len(batch)}/{len(points)}...", flush=True)
        
        # Retrieving elevation data for each sampled point in iteration.
        elev_response = retry_session.get(
            "https://api.open-meteo.com/v1/elevation",
            params={"latitude": ",".join(map(str, batch["lat"])),
                    "longitude": ",".join(map(str, batch["lon"]))},
        )
        elev_response.raise_for_status()
        elevations += elev_response.json()["elevation"]
    points["elevation"] = elevations



    # Merging sampled points into ERA5 grid cells (0.25 degrees). Each cell is
    # requested once, at the mean position and mean elevation of the sampled
    # points inside it. "weight" is the number of sampled points in the cell.
    # This saves API weighted cost, making the retrieval possible with the
    # API's free plan data limits.
    points["cell_lat"] = (points["lat"] / 0.25).round() * 0.25
    points["cell_lon"] = (points["lon"] / 0.25).round() * 0.25
    
    # Defining cells to be called at mean of lon/lat and elevation.
    cells = points.groupby(["cell_lat", "cell_lon"]).agg(
        lat=("lat", "mean"), lon=("lon", "mean"),
        elevation=("elevation", "mean"), weight=("lat", "size"),
    ).reset_index()
    print(f"Merged {len(points)} points into {len(cells)} ERA5 cells.", flush=True)



    # Setting up chunk-based API data requesting (lots of data).
    chunk_size = 10
    total_chunks = (len(cells) + chunk_size - 1) // chunk_size

    # Iterating over each chunk.
    for chunk_number, chunk_start in enumerate(
        range(0, len(cells), chunk_size), start=1):
        
        chunk = cells.iloc[chunk_start:chunk_start + chunk_size]

        # Defining parameters as instructed by Open-Meteo API.
        params = {
            "latitude": chunk["lat"].tolist(),
            "longitude": chunk["lon"].tolist(),
            "elevation": chunk["elevation"].tolist(),
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ["temperature_2m", "precipitation"],
            "models": "era5",
            "timezone": "Europe/Berlin",}

        # Printing progress messages (long code execution times).
        print(
            f"Attempting chunk {chunk_number}/{total_chunks} "
            f"({len(chunk)} cells) for region {region}...",
            flush=True,)



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
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ).tz_convert(response.Timezone().decode()),

                # Defining temp. and precip. key:value pairs for soon-to-exist df.
                "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
                "precipitation": hourly.Variables(1).ValuesAsNumpy(),}

            # Converting data dictionary to pandas df.
            point_data = pd.DataFrame(data=hourly_data)
            point_data["latitude"] = cell["lat"]
            point_data["longitude"] = cell["lon"]
            point_data["elevation"] = cell["elevation"]
            point_data["weight"] = int(cell["weight"])
            region_data.append(point_data)

        print(f"Completed chunk {chunk_number}/{total_chunks}.", flush=True)

        # Pausing between chunks to stay under the API's per-minute limit.
        time.sleep(10)

    # Saving everything to csv so the API call only needs to be done once.
    region_data = pd.concat(region_data, ignore_index=True)
    region_data.to_csv(csv_file, index=False)
    print(f"Saved {len(region_data)} rows to {csv_file}.", flush=True)
    return region_data

no3_2024 = download_region("NO 3", "2024-01-01", "2024-12-31")

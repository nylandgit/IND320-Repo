# This code has been copied and adapted from Kristian Hovde Lilands IND320
# lecture held at NMBU on 26.10.2026.

import geopandas as gpd
import pandas as pd

def sampling_areas_el(n=1000):
    
    # Reading relevant shapefile.
    gdf_el = gpd.read_file("Oblig/shapefiles/electricity areas/Budområder.shp")

    # Generating random points for sampling as instructed.
    points_el = gdf_el['geometry'].sample_points(size=n, random_state=42)

    # Transforming WGS84 (EPSG:4326) for latitude and longitude.
    points_wgs84_el = points_el.to_crs(epsg=4326)

    # Extracting and saving coordinates.
    locations_by_region_el = {}
    for idx_el, multipoint_el in points_wgs84_el.items():
        region_name_el = gdf_el.loc[idx_el, 'budomr']
        print(f"Region: {region_name_el}")

        for point_el in multipoint_el.geoms:
            lat_el = point_el.y
            lon_el = point_el.x
            locations_by_region_el.setdefault(region_name_el, []).append((lat_el, lon_el))

    return locations_by_region_el

#print(df_el.head())

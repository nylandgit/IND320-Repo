# Ran once.
from pathlib import Path

import geopandas as gpd

SRC, OUT = Path("shapefiles"), Path("geojson")
OUT.mkdir(exist_ok=True)

FILES = {
    "electricity areas/Budområder.shp": "electricity_areas",
    "precipitation areas/NVE_Region.shp": "precipitation_areas",
}

for shp, name in FILES.items():
    gdf = gpd.read_file(SRC / shp)
    if gdf.crs is None:  # same assumption as the original code
        gdf = gdf.set_crs(epsg=25833)
    gdf = gdf.to_crs(epsg=4326)
    gdf["geometry"] = gdf.geometry.simplify(0.001)  # ~100 m; keeps the file small
    gdf.to_file(OUT / f"{name}.geojson", driver="GeoJSON")
    print("wrote", OUT / f"{name}.geojson")

import pandas as pd
import geopandas as gpd
from pathlib import Path

from tqdm import tqdm

dataToMerge = []
for f in tqdm(list(Path("/home/starsep/Downloads/BUIB").iterdir())):
    if not f.name.endswith(".shp"):
        continue
    gdf = gpd.read_file(f)
    trainPlatforms = gdf[gdf["RODZAJ"] == "peronKolejowy"]
    trainPlatforms = trainPlatforms.to_crs("WGS84")
    dataToMerge.append(trainPlatforms)

gdf = gpd.GeoDataFrame(pd.concat(dataToMerge))
gdf.to_file("DATA.geojson", driver="GeoJSON", crs="WGS84")
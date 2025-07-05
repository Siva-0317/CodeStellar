from rasterstats import zonal_stats
import geopandas as gpd
import os

zones_path = "data/processed/chennai_boundary.shp"
features = ["slope", "aspect", "hillshade"]

for feat in features:
    feat_path = f"data/processed/{feat}.tif"
    stats = zonal_stats(zones_path, feat_path, stats=["mean", "min", "max"], geojson_out=True)
    gdf = gpd.GeoDataFrame.from_features(stats)
    gdf.to_file(f"data/processed/zonal_stats_{feat}.geojson", driver="GeoJSON")
    print(f"Saved: data/processed/zonal_stats_{feat}.geojson")

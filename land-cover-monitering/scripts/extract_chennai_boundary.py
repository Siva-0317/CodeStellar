import geopandas as gpd
import os

# Path to GADM Level 2 shapefile (adjust if needed)
shapefile_path = "data/raw/gadm41_IND_2.shp"

# Load the shapefile
gdf = gpd.read_file(shapefile_path)

# Filter for Chennai district (Tamil Nadu)
chennai_gdf = gdf[gdf['NAME_2'].str.lower() == 'chennai']

# Output path
output_path = "data/processed/chennai_boundary.shp"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save the extracted Chennai boundary
chennai_gdf.to_file(output_path)

print(f"✅ Chennai boundary saved to: {output_path}")

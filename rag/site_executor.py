import json
import rasterio
import numpy as np
import os
from rasterio.mask import mask
from whitebox.whitebox_tools import WhiteboxTools
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import osmnx as ox

# === FIXED PATHS ===
UPLOADS_DIR = os.path.abspath("rag/uploads")
OUTPUT_DIR = os.path.abspath("rag/outputs")
GEOJSON_DIR = os.path.abspath("rag/geojson")

# === OUTPUT FILES ===
CLIPPED_TIF_PATH = os.path.join(OUTPUT_DIR, "clipped_input.tif")
SLOPE_TIF_PATH = os.path.join(OUTPUT_DIR, "slope.tif")
SUITABILITY_TIF_PATH = os.path.join(OUTPUT_DIR, "site_suitability.tif")
MAP_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "site_suitability_map.png")

# === SETUP ===
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GEOJSON_DIR, exist_ok=True)

wbt = WhiteboxTools()
wbt.set_working_dir(OUTPUT_DIR)

def download_boundary(location_name):
    geojson_path = os.path.join(GEOJSON_DIR, f"{location_name.lower().replace(',', '').replace(' ', '_')}_boundary.geojson")
    gdf = ox.geocode_to_gdf(location_name)
    gdf.to_file(geojson_path, driver="GeoJSON")
    return gdf, geojson_path

def run_site_suitability_workflow(location_name: str, uploaded_tif: str):
    print(f"\n📍 Region: {location_name}\n📄 DEM File: {uploaded_tif}")

    # === STEP 1: Download GeoJSON ===
    print("📥 Downloading boundary...")
    boundary_gdf, geojson_path = download_boundary(location_name)
    print(f"✅ Saved boundary: {geojson_path}")

    # === STEP 2: Clip DEM ===
    print("🔍 Clipping DEM with boundary...")
    with rasterio.open(uploaded_tif) as src:
        boundary_gdf = boundary_gdf.to_crs(src.crs)
        geojson_geom = boundary_gdf.geometry.values[0]
        try:
            clipped, transform = mask(src, [geojson_geom], crop=True)
        except ValueError:
            raise ValueError(f"❌ The uploaded DEM does not overlap with {location_name}. Please upload a matching DEM.")
        meta = src.meta.copy()

    meta.update({"height": clipped.shape[1], "width": clipped.shape[2], "transform": transform})
    with rasterio.open(CLIPPED_TIF_PATH, "w", **meta) as dst:
        dst.write(clipped)
    print(f"✅ Clipped DEM saved to: {CLIPPED_TIF_PATH}")

    # === STEP 3: Slope using WhiteboxTools ===
    print("📐 Calculating slope...")
    wbt.slope(dem=CLIPPED_TIF_PATH, output=SLOPE_TIF_PATH, units="degrees")
    print(f"✅ Slope saved to: {SLOPE_TIF_PATH}")

    # === STEP 4: Elevation + Slope to Site Suitability ===
    print("⚙️ Generating site suitability map...")
    with rasterio.open(CLIPPED_TIF_PATH) as elev_src:
        elevation = elev_src.read(1)
        elev_meta = elev_src.meta.copy()

    with rasterio.open(SLOPE_TIF_PATH) as slope_src:
        slope = slope_src.read(1)

    # === Classification ===
    elevation_masked = np.where(elevation <= 0, np.nan, elevation)
    suitability = np.zeros_like(elevation, dtype=np.uint8)

    suitability[np.where((elevation_masked >= 0) & (elevation_masked < 5))] += 1
    suitability[np.where((elevation_masked >= 5) & (elevation_masked < 20))] += 2
    suitability[np.where((elevation_masked >= 20) & (elevation_masked < 50))] += 3
    suitability[np.where((elevation_masked >= 50) & (elevation_masked < 100))] += 4
    suitability[np.where(elevation_masked >= 100)] += 5

    suitability[np.where((slope >= 0) & (slope < 5))] += 5
    suitability[np.where((slope >= 5) & (slope < 15))] += 3
    suitability[np.where(slope >= 15)] += 1

    suitability = np.nan_to_num(suitability, nan=0)
    suitability = np.clip(suitability // 2, 1, 5)

    elev_meta.update(dtype=rasterio.uint8, count=1, nodata=0)
    with rasterio.open(SUITABILITY_TIF_PATH, "w", **elev_meta) as dst:
        dst.write(suitability, 1)

    print(f"✅ Site suitability raster saved to: {SUITABILITY_TIF_PATH}")

    # === VISUALIZE ===
    print("🖼️ Rendering map image...")
    cmap = ListedColormap(["gray", "lightyellow", "khaki", "darkseagreen", "forestgreen"])
    labels = ["Very Low", "Low", "Moderate", "High", "Very High"]
    plt.figure(figsize=(8, 5))
    im = plt.imshow(suitability, cmap=cmap)
    cbar = plt.colorbar(im, ticks=[1, 2, 3, 4, 5])
    cbar.ax.set_yticklabels(labels)
    plt.title("Site Suitability Map")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(MAP_OUTPUT_PATH)
    plt.close()
    print(f"✅ Map image saved to: {MAP_OUTPUT_PATH}")

if __name__ == "__main__":
    # Example usage for direct test:
    with open(os.path.join("rag", "workflows", "sample_workflow.json")) as f:
        workflow = json.load(f)
    location_name = None
    for step in workflow.get("workflow", []):
        if "task" in step and "site suitability" in step["task"].lower():
            # Extract location from the task string, e.g., "site suitability for Kochi"
            task = step["task"]
            if "for" in task:
                location_name = task.split("for", 1)[1].strip()
            else:
                location_name = "Vellore, India"  # fallback
            break
    if not location_name:
        location_name = "Vellore, India"  # fallback

    # Find the uploaded tif file path from workflow JSON
    uploaded_tif = None
    for step in workflow.get("workflow", []):
        args = step.get("args", {})
        if "input_file" in args:
            uploaded_tif = args["input_file"]
            break
    if not uploaded_tif:
        uploaded_tif = "rag/uploads/input_20250706_130716.tif"  # fallback

    run_site_suitability_workflow(location_name=location_name, uploaded_tif=uploaded_tif)

import json
import rasterio
import numpy as np
import os
from rasterio.enums import Resampling
from rasterio.plot import show
from whitebox.whitebox_tools import WhiteboxTools
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import osmnx as ox
import geopandas as gpd
from rasterio.mask import mask

UPLOAD_DIR = os.path.abspath("rag/uploads")
OUTPUT_DIR = os.path.abspath("rag/outputs")
GEOJSON_DIR = os.path.abspath("rag/geojson")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GEOJSON_DIR, exist_ok=True)

wbt = WhiteboxTools()
wbt.set_working_dir(UPLOAD_DIR)

def download_boundary(location_name):
    geojson_path = os.path.join(GEOJSON_DIR, f"{location_name.lower().replace(',', '').replace(' ', '_')}_boundary.geojson")
    gdf = ox.geocode_to_gdf(location_name)
    gdf.to_file(geojson_path, driver="GeoJSON")
    return gdf, geojson_path

def run_workflow(json_path):
    with open(json_path) as f:
        workflow = json.load(f)["workflow"]

    location = ""
    for step in workflow:
        if "task" in step and "flood-prone" in step["task"].lower():
            location = step["task"].split("for")[-1].strip()
            break

    if not location:
        raise ValueError("❌ No location found in task description.")

    print(f"\n📍 Region: {location}")

    # Download boundary and clip DEM
    print("📥 Downloading boundary...")
    boundary_gdf, geojson_path = download_boundary(location)
    print(f"✅ Saved boundary: {geojson_path}")

    for step in workflow:
        args = step.get("args", {})
        tool = args.get("tool", "").lower()
        action = step["action"]
        input_path = os.path.join("rag/uploads", os.path.basename(args["input_file"]))
        output_path = os.path.join("rag/outputs", os.path.basename(args["output_file"]))

        print(f"\n🔧 Step: {action}\n  ➤ Input: {input_path}\n  ➤ Output: {output_path}")

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"❌ Input file not found: {input_path}")

        if "clip" in action.lower():
            with rasterio.open(input_path) as src:
                boundary_gdf = boundary_gdf.to_crs(src.crs)
                geojson_geom = boundary_gdf.geometry.values[0]
                try:
                    clipped, transform = mask(src, [geojson_geom], crop=True)
                except ValueError:
                    raise ValueError(f"❌ The DEM does not overlap with {location}.")
                meta = src.meta.copy()
            meta.update({"height": clipped.shape[1], "width": clipped.shape[2], "transform": transform})
            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(clipped)
            continue

        if tool == "whiteboxtools":
            if "fill_depressions" in action.lower():
                wbt.fill_depressions(input_path, output_path)
            elif "flow_accumulation" in action.lower():
                wbt.d8_pointer(input_path, os.path.join("rag", "flow_direction.tif"))
                wbt.run_tool(
                    "D8FlowAccumulation",
                    [f"--dem={input_path}", f"--output={output_path}", "--out_type=cells"]
                )

        elif tool == "rasterio":
            with rasterio.open(input_path) as src:
                flow = src.read(1)
                meta = src.meta.copy()

            # Calculate thresholds
            LOW, MEDIUM, HIGH = np.percentile(flow[flow > 0], [70, 85, 95])

            # Set all as NoData initially
            risk = np.full_like(flow, 255, dtype=np.uint8)

            # Classify only valid data
            risk[(flow > 0) & (flow <= LOW)] = 0  # Safe
            risk[(flow > LOW) & (flow <= MEDIUM)] = 1  # Low
            risk[(flow > MEDIUM) & (flow <= HIGH)] = 2  # Medium
            risk[flow > HIGH] = 3  # High

            meta.update(dtype=rasterio.uint8, count=1, nodata=255)
            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(risk, 1)

            # Save visual
            cmap = ListedColormap(["lightgray", "yellow", "orange", "red"])
            labels = ["Safe", "Low", "Medium", "High"]

            plt.figure(figsize=(8, 5))
            masked_risk = np.ma.masked_where(risk == 255, risk)
            im = plt.imshow(masked_risk, cmap=cmap, vmin=0, vmax=3)
            cbar = plt.colorbar(im, ticks=[0, 1, 2, 3])
            cbar.ax.set_yticklabels(labels)
            plt.title("Flood Risk Zones")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig("rag/flood_risk_map.png")
            plt.close()

if __name__ == "__main__":
    run_workflow("rag/workflows/sample_workflow.json")

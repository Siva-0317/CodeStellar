import rasterio
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

UPLOAD_DIR = "rag/uploads"
OUTPUT_DIR = "rag/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Filenames must contain band identifiers
required_bands = {"B02": None, "B03": None, "B04": None, "B08": None}

# --- Locate JP2 band files ---
for file in os.listdir(UPLOAD_DIR):
    for band in required_bands:
        if band in file and file.endswith(".jp2"):
            required_bands[band] = os.path.join(UPLOAD_DIR, file)

if None in required_bands.values():
    missing = [b for b, v in required_bands.items() if v is None]
    raise FileNotFoundError(f"❌ Missing bands: {missing}")

print("🔁 Stacking bands into multiband GeoTIFF...")
bands = []
for band_name in ["B02", "B03", "B04", "B08"]:
    with rasterio.open(required_bands[band_name]) as src:
        band_data = src.read(1)
        bands.append(band_data)
        profile = src.profile

stacked = np.stack(bands)
profile.update(count=4,driver="GTiff")
stacked_tif = os.path.join(OUTPUT_DIR, "sentinel_stacked.tif")
with rasterio.open(stacked_tif, "w", **profile) as dst:
    dst.write(stacked)
print(f"✅ Stacked image saved: {stacked_tif}")

# --- NDVI & LULC ---
print("🌱 Computing NDVI and classifying into 5 LULC classes...")

blue, green, red, nir = stacked
ndvi = (nir.astype("float32") - red) / (nir + red + 1e-6)

# Save NDVI
ndvi_tif = os.path.join(OUTPUT_DIR, "ndvi.tif")
meta = profile.copy()
meta.update(count=1, dtype=rasterio.float32)
with rasterio.open(ndvi_tif, "w", **meta) as dst:
    dst.write(ndvi, 1)

# --- LULC Classification ---
lulc = np.zeros_like(ndvi, dtype=np.uint8)
lulc[ndvi < 0.0] = 1         # Water
lulc[(ndvi >= 0.0) & (ndvi < 0.2)] = 2   # Barren
lulc[(ndvi >= 0.2) & (ndvi < 0.4)] = 3   # Built-up
lulc[(ndvi >= 0.4) & (ndvi < 0.6)] = 4   # Sparse Vegetation
lulc[ndvi >= 0.6] = 5                   # Dense Vegetation

# Save LULC raster
lulc_tif = os.path.join(OUTPUT_DIR, "lulc_class.tif")
meta.update(dtype=rasterio.uint8)
with rasterio.open(lulc_tif, "w", **meta) as dst:
    dst.write(lulc, 1)

# --- Plot ---
cmap = ListedColormap(["blue", "tan", "gray", "yellowgreen", "green"])
labels = ["Water", "Barren", "Built-up", "Sparse Veg", "Dense Veg"]
colors = dict(zip(range(1, 6), labels))

plt.figure(figsize=(10, 6))
im = plt.imshow(lulc, cmap=cmap, vmin=1, vmax=5)
cbar = plt.colorbar(im, ticks=[1, 2, 3, 4, 5])
cbar.ax.set_yticklabels(labels)
plt.title("Land Use / Land Cover Classification")
plt.axis("off")
plt.tight_layout()

lulc_map = os.path.join(OUTPUT_DIR, "lulc_map.png")
plt.savefig(lulc_map)
plt.close()

print(f"🗺️ LULC Map saved to: {lulc_map}")

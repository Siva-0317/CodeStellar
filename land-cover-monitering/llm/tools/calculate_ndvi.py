import rasterio
import numpy as np
from rasterio.plot import show
from rasterio.enums import Resampling

# Paths
b04_path = "data/raw/sentinel_chennai/B04.jp2"
b08_path = "data/raw/sentinel_chennai/B08.jp2"
ndvi_output = "data/processed/ndvi.tif"

# Open Red (B04) and NIR (B08)
with rasterio.open(b04_path) as red_src:
    red = red_src.read(1).astype('float32')
    red_meta = red_src.meta.copy()

with rasterio.open(b08_path) as nir_src:
    nir = nir_src.read(1).astype('float32')

# Avoid division by zero
ndvi = (nir - red) / (nir + red + 1e-6)

# Update metadata for output NDVI
red_meta.update(
    driver='GTiff',
    dtype='float32',
    count=1
)

# Save NDVI
with rasterio.open(ndvi_output, 'w', **red_meta) as dst:
    dst.write(ndvi, 1)


print("✅ NDVI saved to:", ndvi_output)

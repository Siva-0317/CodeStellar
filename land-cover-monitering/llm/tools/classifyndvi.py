import rasterio
import numpy as np

ndvi_path = "data/processed/ndvi.tif"
output_path = "data/processed/land_cover_classified.tif"

# Read NDVI
with rasterio.open(ndvi_path) as src:
    ndvi = src.read(1)
    meta = src.meta.copy()

# Classification logic
classified = np.zeros(ndvi.shape, dtype=np.uint8)
classified[ndvi < 0.1] = 1         # Water
classified[(ndvi >= 0.1) & (ndvi < 0.2)] = 2  # Barren
classified[(ndvi >= 0.2) & (ndvi < 0.5)] = 3  # Urban
classified[ndvi >= 0.5] = 4        # Forest

# Update metadata
meta.update(dtype='uint8', count=1)

# Save classified raster
with rasterio.open(output_path, 'w', **meta) as dst:
    dst.write(classified, 1)

print("✅ Classified land cover map saved:", output_path)

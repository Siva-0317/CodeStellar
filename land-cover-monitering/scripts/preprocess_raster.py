import numpy as np
import rasterio
from collections import Counter

with rasterio.open('data/raw/esa_landcover_chennai.tif') as src:

    data = src.read(1)

# Convert to integers (round or cast)
data = np.rint(data).astype(np.uint8)

# Count unique values
unique, counts = np.unique(data, return_counts=True)

for val, count in zip(unique, counts):
    print(f"Class {val}: {count} pixels")

import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Load ESA class dictionary (simplified for this example)
esa_classes = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen"
}

# Load raster
path = "data/raw/esa_landcover_chennai.tif"
with rasterio.open(path) as src:
    landcover = src.read(1)
    transform = src.transform
    pixel_size = transform[0]  # usually 10 meters
    pixel_area_km2 = (pixel_size * pixel_size) / 1e6  # convert m² to km²

# Convert float values to integer classes
landcover = np.round(landcover).astype(np.uint8)

# Get unique values and counts
unique, counts = np.unique(landcover, return_counts=True)
class_stats = dict(zip(unique, counts))

# Prepare summary table
summary = []
for code, count in class_stats.items():
    if code == 0:
        continue  # skip no data if needed
    area = count * pixel_area_km2
    label = esa_classes.get(code, "Unknown")
    summary.append((code, label, count, area))

df = pd.DataFrame(summary, columns=["Class", "Label", "Pixel Count", "Area (km²)"])
df.sort_values("Area (km²)", ascending=False, inplace=True)

# Save as CSV
df.to_csv("chennai_landcover_summary.csv", index=False)
print("✅ Summary saved to chennai_landcover_summary.csv")

# Plot chart
plt.figure(figsize=(10, 6))
plt.bar(df["Label"], df["Area (km²)"])
plt.xticks(rotation=45, ha="right")
plt.title("Land Cover Area Distribution (Chennai)")
plt.ylabel("Area (km²)")
plt.tight_layout()
plt.savefig("chennai_landcover_chart.png", dpi=300)
plt.show()

import rasterio
import matplotlib.pyplot as plt
import os

# Paths to outputs
dem_outputs = {
    "Slope": "data/processed/slope.tif",
    "Aspect": "data/processed/aspect.tif",
    "Hillshade": "data/processed/hillshade.tif"
}

# Plot each raster
for name, path in dem_outputs.items():
    if not os.path.exists(path):
        print(f"Missing: {path}")
        continue

    with rasterio.open(path) as src:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title(name)
        image = src.read(1)
        show = ax.imshow(image, cmap='terrain')
        fig.colorbar(show, ax=ax, orientation='vertical')
        plt.tight_layout()
        plt.show()

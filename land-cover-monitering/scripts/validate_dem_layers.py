import rasterio
import matplotlib.pyplot as plt
import os

base_path = "data/processed"
layers = ["slope.tif", "aspect.tif", "hillshade.tif"]

for layer in layers:
    path = os.path.join(base_path, layer)
    with rasterio.open(path) as src:
        data = src.read(1)
        plt.figure(figsize=(8, 6))
        plt.imshow(data, cmap='terrain')
        plt.title(f"{layer.split('.')[0].capitalize()} Layer")
        plt.colorbar(label=src.units[0] if src.units[0] else 'Value')
        plt.grid(False)
        plt.tight_layout()
        plt.show()

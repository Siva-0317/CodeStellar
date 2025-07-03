import rasterio

with rasterio.open("output_hh.tif") as src:
    print("CRS:", src.crs)
    print("Shape:", src.width, "x", src.height)
    print("Min:", src.read(1).min())
    print("Max:", src.read(1).max())

import rasterio
import matplotlib.pyplot as plt

with rasterio.open("rag/output_hh.tif") as src:
    plt.imshow(src.read(1), cmap="Blues")
    plt.title("Flood Prone Zones")
    plt.colorbar()
    plt.show()
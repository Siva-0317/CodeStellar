import rasterio
import matplotlib.pyplot as plt

path = "data/raw/esa_landcover_chennai.tif"

with rasterio.open(path) as src:
    landcover = src.read(1)
    plt.imshow(landcover, cmap='tab20')
    plt.title("Chennai Land Cover")
    plt.colorbar(label="Land Cover Class")
    plt.show()

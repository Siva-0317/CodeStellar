import rasterio

# Path to SRTM DEM
path = "data/raw/strm_30m_chennai.tif"


with rasterio.open(path) as src:
    print("✅ File successfully opened")
    print(f"CRS: {src.crs}")
    print(f"Resolution: {src.res}")
    print(f"Width, Height: {src.width}, {src.height}")
    print(f"Bounds: {src.bounds}")

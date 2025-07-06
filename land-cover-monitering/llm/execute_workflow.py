import json
import subprocess
import rasterio
import numpy as np

def calculate_ndvi(red_path, nir_path, output_path):
    with rasterio.open(red_path) as red_src:
        red = red_src.read(1).astype('float32')
        meta = red_src.meta.copy()

    with rasterio.open(nir_path) as nir_src:
        nir = nir_src.read(1).astype('float32')

    ndvi = (nir - red) / (nir + red + 1e-6)
    meta.update(driver='GTiff', dtype='float32', count=1)

    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(ndvi, 1)

    print(" NDVI calculated and saved:", output_path)

def classify_land_cover(ndvi_path, output_path):
    with rasterio.open(ndvi_path) as src:
        ndvi = src.read(1)
        meta = src.meta.copy()

    classified = np.zeros(ndvi.shape, dtype=np.uint8)
    classified[ndvi < 0.1] = 1
    classified[(ndvi >= 0.1) & (ndvi < 0.2)] = 2
    classified[(ndvi >= 0.2) & (ndvi < 0.5)] = 3
    classified[ndvi >= 0.5] = 4

    meta.update(dtype='uint8', count=1)

    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(classified, 1)

    print("Land cover classified and saved:", output_path)

def execute_workflow(workflow_file):
    with open(workflow_file, 'r') as f:
        workflow = json.load(f)

    for step in workflow['steps']:
        tool = step['tool']
        if tool == "CalculateNDVI":
            calculate_ndvi(step['input']['red'], step['input']['nir'], step['output'])
        elif tool == "ClassifyLandCover":
            classify_land_cover(step['input'], step['output'])
        else:
            print(f" Unknown tool: {tool}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python execute_workflow.py <workflow_file>")
        sys.exit(1)
    execute_workflow(sys.argv[1])

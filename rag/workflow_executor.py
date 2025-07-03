import json
import rasterio
import numpy as np
import os
from rasterio.enums import Resampling
from rasterio.plot import show
from whitebox.whitebox_tools import WhiteboxTools
import matplotlib.pyplot as plt

wbt = WhiteboxTools()
wbt.set_working_dir("rag")  # Workspace folder for outputs

def visualize_tif(tif_path, title="Raster Output", cmap="terrain", colorbar_label="Value"):
    with rasterio.open(tif_path) as src:
        array = src.read(1, resampling=Resampling.bilinear)
        plt.figure(figsize=(10, 8))
        plt.imshow(array, cmap=cmap)
        plt.title(title)
        plt.colorbar(label=colorbar_label)
        plt.axis('off')
        plt.tight_layout()
        plt.show()

def execute_action(action):
    args = action['args']
    tool = args['tool'].lower()

    if action['action'].lower() == "load dem data":
        return args['input_file']

    elif tool == 'whiteboxtools':
        input_file = args['input_file']
        output_file = args['output_file']

        if "fill sinks" in action['action'].lower():
            wbt.fill_depressions(dem=input_file, output=output_file)
        elif "flow accumulation" in action['action'].lower():
            wbt.d8_flow_accumulation(input_file=input_file, output=output_file, out_type="cells")

        return output_file

    elif tool == 'qgis':
        input_file = args['input_file']
        threshold = args.get('threshold', 1000)
        output_file = args['output_file']

        with rasterio.open(input_file) as src:
            data = src.read(1)
            profile = src.profile
            risk = (data > threshold).astype(np.uint8)
            profile.update(dtype=rasterio.uint8, count=1)
            with rasterio.open(output_file, 'w', **profile) as dst:
                dst.write(risk, 1)

        return output_file

    elif tool == 'gdal':
        # Placeholder for GDAL commands
        return "gdal_tool_used_placeholder"

    return None

def run_workflow(json_path):
    with open(json_path) as f:
        workflow = json.load(f)["workflow"]

    output_files = []
    for step in workflow:
        print(f"Executing: {step['action']} using {step['args']['tool']}")
        result = execute_action(step)
        if result: output_files.append(result)

    return output_files

if __name__ == '__main__':
    outputs = run_workflow("rag/sample_workflow.json")
    for path in outputs:
        visualize_tif(path, title=f"Output: {os.path.basename(path)}")

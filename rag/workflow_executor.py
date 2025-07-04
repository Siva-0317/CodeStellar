import json
import rasterio
import numpy as np
import os
from rasterio.enums import Resampling
from rasterio.plot import show
from whitebox.whitebox_tools import WhiteboxTools
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

wbt = WhiteboxTools()
wbt.set_working_dir("rag/uploads")

def run_workflow(json_path):
    with open(json_path) as f:
        workflow = json.load(f)["workflow"]

    for step in workflow:
        args = step.get("args", {})
        tool = args.get("tool", "").lower()
        action = step["action"]
        input_path = os.path.join("rag/uploads", os.path.basename(args["input_file"]))
        output_path = os.path.join("rag/outputs", os.path.basename(args["output_file"]))

        print(f"\n🔧 Step: {action}\n  ➤ Input: {input_path}\n  ➤ Output: {output_path}")

        if tool == "whiteboxtools":
            if "fill_depressions" in action.lower():
                if os.path.exists(input_path):
                    wbt.fill_depressions(input_path, output_path)
                else:
                    raise FileNotFoundError(f"❌ Input DEM not found at {input_path}")

            elif "flow_accumulation" in action.lower():
                if os.path.exists(input_path):
                    wbt.d8_pointer(input_path, os.path.join("rag", "flow_direction.tif"))
                    wbt.run_tool(
                        "D8FlowAccumulation",
                        [f"--dem={input_path}", f"--output={output_path}", "--out_type=cells"]
                    )
                else:
                    raise FileNotFoundError(f"❌ Filled DEM not found at {input_path}")

        elif tool == "rasterio":
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"❌ Flow accumulation file not found: {input_path}")

            with rasterio.open(input_path) as src:
                flow = src.read(1)
                meta = src.meta.copy()

            LOW, MEDIUM, HIGH = np.percentile(flow, [70, 85, 95])
            risk = np.zeros_like(flow, dtype=np.uint8)
            risk[(flow > LOW) & (flow <= MEDIUM)] = 1
            risk[(flow > MEDIUM) & (flow <= HIGH)] = 2
            risk[flow > HIGH] = 3

            meta.update(dtype=rasterio.uint8, count=1, nodata=0)
            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(risk, 1)

            # Save visual
            cmap = ListedColormap(["lightgray", "yellow", "orange", "red"])
            labels = ["Safe", "Low", "Medium", "High"]
            plt.figure(figsize=(8, 5))
            im = plt.imshow(risk, cmap=cmap)
            cbar = plt.colorbar(im, ticks=[0, 1, 2, 3])
            cbar.ax.set_yticklabels(labels)
            plt.title("Flood Risk Zones")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig("rag/flood_risk_map.png")
            plt.close()

if __name__ == "__main__":
    run_workflow("rag/workflows/sample_workflow.json")
# rag/openr_gen.py using OpenRouter via direct HTTP request
import json
import os
import regex as re
import sys
import requests

output_path = "rag/workflows/sample_workflow.json"
cot_path = "rag/llm_response.txt"

# OpenRouter API details
API_KEY = "your-api-key"
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_workflow_from_prompt(prompt: str):
    system_prompt = """
You are a GIS workflow generator. Given a user task, generate a concrete JSON workflow using the following schema.
Return the JSON object followed by your step-by-step reasoning (Chain-of-Thought) explaining how you constructed the workflow.

Schema:
{
  "workflow": [
    {
      "task": string,
      "action": string,
      "args": {
        "tool": one of [whiteboxtools, qgis, gdal, rasterio, osmnx, ndvi],
        "input_file": string,
        "output_file": string
      }
    }
  ]
}

Examples:

Generate flood prone zones from DEM for Chennai:
{
  "workflow": [
    {
      "task": "hydrology",
      "action": "Fill depressions",
      "args": {
        "tool": "whiteboxtools",
        "input_file": "uploads/input.tif",
        "output_file": "filled_dem.tif"
      }
    },
    {
      "task": "hydrology",
      "action": "Calculate flow accumulation",
      "args": {
        "tool": "whiteboxtools",
        "input_file": "filled_dem.tif",
        "output_file": "flow_accum.tif"
      }
    },
    {
      "task": "risk_analysis",
      "action": "Classify flood risk",
      "args": {
        "tool": "rasterio",
        "input_file": "flow_accum.tif",
        "output_file": "flood_risk_levels.tif"
      }
    }
  ]
}

Generate site suitability map from DEM for Chennai:
{
  "workflow": [
    {
      "task": "boundary",
      "action": "Download city boundary",
      "args": {
        "tool": "osmnx",
        "input_file": "Chennai",
        "output_file": "chennai_boundary.geojson"
      }
    },
    {
      "task": "preprocessing",
      "action": "Clip DEM using boundary",
      "args": {
        "tool": "rasterio",
        "input_file": "uploads/input.tif",
        "output_file": "clipped_chennai.tif"
      }
    },
    {
      "task": "terrain",
      "action": "Calculate slope",
      "args": {
        "tool": "whiteboxtools",
        "input_file": "clipped_chennai.tif",
        "output_file": "chennai_slope.tif"
      }
    },
    {
      "task": "suitability",
      "action": "Classify elevation and slope",
      "args": {
        "tool": "rasterio",
        "input_file": "clipped_chennai.tif",
        "output_file": "site_suitability.tif"
      }
    }
  ]
}

Generate land cover classification from Sentinel-2 bands for Chennai:
{
  "workflow": [
    {
      "task": "landcover",
      "action": "Stack Sentinel bands B02, B03, B04, B08",
      "args": {
        "tool": "rasterio",
        "input_file": "uploads/B02,B03,B04,B08.jp2",
        "output_file": "sentinel_stacked.tif"
      }
    },
    {
      "task": "landcover",
      "action": "Compute NDVI",
      "args": {
        "tool": "rasterio",
        "input_file": "sentinel_stacked.tif",
        "output_file": "ndvi.tif"
      }
    },
    {
      "task": "landcover",
      "action": "Classify LULC from NDVI",
      "args": {
        "tool": "rasterio",
        "input_file": "ndvi.tif",
        "output_file": "lulc_class.tif"
      }
    }
  ]
}

After the JSON, add reasoning like:
Reasoning:
1. Since the task involves DEM, we first fill depressions.
2. Then calculate flow accumulation...
3. Classify using raster thresholds, etc.
"""
    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": prompt.strip()}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise RuntimeError(f"❌ Request failed: {response.status_code} - {response.text}")

    result = response.json()
    full_response = result["choices"][0]["message"]["content"]

    # Save full CoT reasoning
    with open(cot_path, "w", encoding="utf-8") as f:
        f.write(full_response.strip())

    # Extract JSON from response
    json_blocks = re.findall(r"\{(?:[^{}]|(?R))*\}", full_response, re.DOTALL)
    snippet = json_blocks[0] if json_blocks else ""

    if not snippet.strip():
        raise ValueError("No JSON object found.")

    workflow_data = json.loads(snippet)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow_data, f, indent=2)

    print("✅ Workflow saved.")
    print(f"📘 Reasoning saved to: {cot_path}")

# Entry point
if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt_text = " ".join(sys.argv[1:])
        get_workflow_from_prompt(prompt_text)
    else:
        print("❌ Please provide prompt as command-line argument.")

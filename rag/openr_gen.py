# rag/generate_workflow.py using OpenRouter
import json
import os
import regex as re
import sys
from openai import OpenAI

output_path = "rag/workflows/sample_workflow.json"

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="yourapikey"  # Replace with your actual key
)

def get_workflow_from_prompt(prompt: str):
    system_prompt = """
You are a GIS workflow generator. Given a user task, generate a concrete JSON workflow using the following schema.
Return ONLY the JSON object.

Schema:
{
  "workflow": [
    {
      "task": string,
      "action": string,
      "args": {
        "tool": one of [whiteboxtools, qgis, gdal, rasterio, osmnx],
        "input_file": string,
        "output_file": string
      }
    }
  ]
}

Examples:

Generate flood prone zones from DEM:
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
"""

    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": prompt.strip()}
    ]

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat:free",
        messages=messages,
        temperature=0.7,
    )

    text = response.choices[0].message.content

    json_blocks = re.findall(r"\{(?:[^{}]|(?R))*\}", text, re.DOTALL)
    snippet = json_blocks[0] if json_blocks else ""

    if not snippet.strip():
        raise ValueError("No JSON object found.")

    data = json.loads(snippet)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Workflow saved.")

# 🟨 Use sys.argv for prompt (for Streamlit compatibility)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt_text = " ".join(sys.argv[1:])
        get_workflow_from_prompt(prompt_text)
    else:
        print("❌ Please provide prompt as command-line argument.")

# rag/generate_workflow.py
import json
import os
import regex as re
import sys
from llama_cpp import Llama

model_path = "D:/AI/lmstudio-community/Llama-3.2-3B-Instruct-GGUF/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
output_path = "rag/workflows/sample_workflow.json"

def get_workflow_from_prompt(prompt: str):
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=4,
        seed=1337
    )

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
        "tool": one of [whiteboxtools, qgis, gdal, rasterio],
        "input_file": string,
        "output_file": string
      }
    }
  ]
}

Example: Generate flood prone zones from DEM:
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
"""

    prompt_input = f"[INST] {system_prompt.strip()} Task: {prompt.strip()} [/INST]"
    resp = llm.create_completion(
        prompt=prompt_input,
        max_tokens=1024,
        temperature=0.7,
        stop=["</s>", "[INST]"]
    )
    text = resp["choices"][0]["text"]

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

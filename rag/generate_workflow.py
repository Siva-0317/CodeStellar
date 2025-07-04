import json
import os
import regex as re
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
Return ONLY the JSON object, filled with realistic values for the user's task. Do NOT return a template or placeholders.

Schema:
{
  "workflow": [
    {
      "task": string,
      "action": string,
      "args": {
        "tool": one of [whiteboxtools, qgis, gdal, geopandas, rasterio],
        "function": valid function name,
        "input": string path,
        "output": string path,
        ...optional parameters...
      }
    }
  ]
}

Example for "Show me flood-prone zones in Chennai using DEM data":
{
  "workflow": [
    {
      "task": "preprocessing",
      "action": "Fill sinks in DEM",
      "args": {
        "tool": "whiteboxtools",
        "function": "fill_depressions_wang_and_liu",
        "input": "uploads/chennai_dem.tif",
        "output": "outputs/filled_dem.tif"
      }
    },
    {
      "task": "hydrology",
      "action": "Calculate flow accumulation",
      "args": {
        "tool": "whiteboxtools",
        "function": "flow_accumulation",
        "input": "outputs/filled_dem.tif",
        "output": "outputs/flow_accum.tif"
      }
    },
    {
      "task": "analysis",
      "action": "Extract flood-prone zones",
      "args": {
        "tool": "qgis",
        "function": "raster_threshold",
        "input": "outputs/flow_accum.tif",
        "output": "outputs/flood_zones.tif",
        "threshold": 1000
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
        stop=["</s>", "[/INST]"]
    )
    text = resp["choices"][0]["text"]
    print("=== Model Output ===")
    print(text)

    # Extract the first JSON object using regex
    json_blocks = re.findall(r"\{(?:[^{}]|(?R))*\}", text, re.DOTALL)
    snippet = json_blocks[0] if json_blocks else ""

    print("=== Extracted JSON ===")
    print(snippet)

    if not snippet.strip():
        raise ValueError("No JSON object found in model output.")

    try:
        data = json.loads(snippet)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON. The model output may be truncated or malformed.")
        raise e

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Workflow saved to {output_path}")

if __name__ == "__main__":
    user_prompt = input("📝 Enter your geospatial task prompt: ")
    get_workflow_from_prompt(user_prompt)
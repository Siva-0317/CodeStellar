import json
from pathlib import Path

# Paths
prompt_path = Path("llm/prompts/input.txt")
template_path = Path("llm/cot_templates/landcover_cot.txt")
output_path = Path("llm/workflows/workflow1.json")

def load_prompt():
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def load_template():
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def simulate_llm_response(prompt, template):
    reasoning = f"""Step-by-step reasoning:
1. Use Band 4 (Red) and Band 8 (NIR) to compute NDVI.
2. Classify NDVI into land cover types:
   - Water (NDVI < 0.1)
   - Barren (0.1–0.2)
   - Urban (0.2–0.5)
   - Forest (NDVI > 0.5)
3. Output classified raster.

Workflow JSON:"""

    workflow = {
        "steps": [
            {
                "tool": "CalculateNDVI",
                "input": {
                    "red": "data/raw/sentinel_chennai/B04.jp2",
                    "nir": "data/raw/sentinel_chennai/B08.jp2"
                },
                "output": "data/processed/ndvi.tif"
            },
            {
                "tool": "ClassifyLandCover",
                "input": "data/processed/ndvi.tif",
                "output": "data/processed/land_cover_classified.tif"
            }
        ]
    }

    return reasoning, workflow

def save_workflow_json(workflow):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=4)
    print(f"✅ Workflow saved to {output_path}")

def main():
    prompt = load_prompt()
    template = load_template()

    reasoning, workflow = simulate_llm_response(prompt, template)
    print("\n--- Chain of Thought Reasoning ---")
    print(reasoning)

    save_workflow_json(workflow)

if __name__ == "__main__":
    main()

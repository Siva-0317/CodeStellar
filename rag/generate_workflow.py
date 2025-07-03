# rag/generate_workflow.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import torch

model_name = "mistralai/Mistral-7B-Instruct-v0.3"

print("Loading model... This may take a few minutes on first run.")

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
except Exception as e:
    print("❌ Tokenizer failed to load. Make sure sentencepiece and tokenizers are installed.")
    print(e)
    exit()

try:
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )
except Exception as e:
    print("❌ Model failed to load.")
    print(e)
    exit()
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def get_workflow_from_prompt(prompt: str):
    system_prompt = (
        "You are a GIS assistant. Given a geospatial analysis task, output a valid JSON workflow. "
        "Each step must have an 'action' and an 'args' dict that includes a 'tool'. "
        "Supported tools: 'whiteboxtools', 'qgis', 'gdal', 'geopandas', 'rasterio'. "
        "Example actions: 'Fill sinks in DEM', 'Calculate flow accumulation', 'Overlay flood map', 'Visualize raster'."
    )
    full_prompt = f"<s>[INST] {system_prompt} Task: {prompt} [/INST]"

    output = generator(full_prompt, max_new_tokens=512, temperature=0.7)[0]["generated_text"]

    # Extract only the JSON part
    json_start = output.find("{")
    json_end = output.rfind("}") + 1
    try:
        json_data = json.loads(output[json_start:json_end])
    except Exception as e:
        print("⚠️ Could not parse JSON from output.")
        print("Raw output:\n", output)
        return

    with open("rag/workflows/sample_workflow.json", "w") as f:
        json.dump(json_data, f, indent=2)

    print("✅ Workflow saved to rag/workflows/sample_workflow.json")

# Example usage
if __name__ == "__main__":
    user_prompt = input("Enter your geospatial task prompt: ")
    get_workflow_from_prompt(user_prompt)

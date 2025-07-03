# rag/generate_workflow.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import torch

model_name = "mistralai/Mistral-7B-Instruct-v0.3"

print("🔄 Loading Mistral model... This may take a few minutes on first run.")

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

def get_workflow_from_prompt(prompt):
    system_prompt = (
        "You are a GIS assistant. Given a geospatial analysis task, output a valid JSON workflow "
        "with tool names and arguments (input_file, output_file, threshold, etc)."
    )
    full_prompt = f"<s>[INST] {system_prompt} Task: {prompt} [/INST]"

    print("\n🚀 Generating workflow...")
    try:
        output = generator(full_prompt, max_new_tokens=512, temperature=0.7)[0]["generated_text"]
    except Exception as e:
        print("❌ Generation failed:", e)
        return

    json_start = output.find("{")
    json_end = output.rfind("}") + 1

    if json_start == -1 or json_end == -1:
        print("⚠️ No JSON detected in output.")
        print("Raw output:\n", output)
        return

    try:
        json_data = json.loads(output[json_start:json_end])
    except Exception as e:
        print("⚠️ Could not parse JSON from output.")
        print("Raw output:\n", output)
        print("Parsing error:", e)
        return

    with open("rag/workflows/sample_workflow.json", "w") as f:
        json.dump(json_data, f, indent=2)

    print("✅ Workflow saved to rag/workflows/sample_workflow.json")

# Example usage
if __name__ == "__main__":
    user_prompt = input("📝 Enter your geospatial task prompt: ")
    get_workflow_from_prompt(user_prompt)

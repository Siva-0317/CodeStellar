# rag/generate_workflow.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json

model_name = "mistralai/Mistral-7B-Instruct-v0.1"

print("Loading model... This may take a few minutes on first run.")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def get_workflow_from_prompt(prompt):
    system_prompt = (
        "You are a GIS assistant. Given a geospatial analysis task, output a valid JSON workflow "
        "with tool names and arguments (input_file, output_file, threshold, etc)."
    )
    full_prompt = f"<s>[INST] {system_prompt} Task: {prompt} [/INST]"

    output = generator(full_prompt, max_new_tokens=512, temperature=0.7)[0]["generated_text"]
    
    # Extract JSON part only
    json_start = output.find("{")
    json_end = output.rfind("}") + 1
    try:
        json_data = json.loads(output[json_start:json_end])
    except:
        print("⚠️ Could not parse JSON from output.")
        print("Raw output:\n", output)
        return

    with open("rag/sample_workflow.json", "w") as f:
        json.dump(json_data, f, indent=2)

    print("✅ Workflow saved to rag/sample_workflow.json")

# Example usage
if __name__ == "__main__":
    user_prompt = input("Enter your geospatial task prompt: ")
    get_workflow_from_prompt(user_prompt)

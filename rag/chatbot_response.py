# chatbot_response.py
from llama_cpp import Llama

# Path to your GGUF model
GEMMA_MODEL_PATH = "D:/AI/gemma-2-2b-it.gguf"  # Replace with actual path

# Initialize LLM once
llm = Llama(
    model_path=GEMMA_MODEL_PATH,
    n_ctx=2048,
    n_threads=4,
    seed=42
)

def chat_with_gemma(user_message):
    prompt = f"[INST] You are a helpful geospatial assistant. {user_message} [/INST]"
    output = llm.create_completion(
        prompt=prompt,
        max_tokens=512,
        temperature=0.7,
        stop=["</s>", "[INST]"]
    )
    return output["choices"][0]["text"].strip()

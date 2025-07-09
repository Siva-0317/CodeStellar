# rag/chatbot_response.py
import sys
from llama_cpp import Llama

# Load once globally (no need to reload per call)
MODEL_PATH = "rag/models/gemma-2-2b-it-Q4_K_M.gguf"
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=6, n_gpu_layers=20)

def generate_response(prompt: str) -> str:
    result = llm(prompt, max_tokens=1024, stop=["User:"])
    return result['choices'][0]['text'].strip()

if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:])
    context = """You are an expert assistant for a geospatial reasoning application. This app allows users to:
- Generate GIS workflows from natural language prompts using LLMs.
- Perform flood-prone zone identification, site suitability analysis, and land use/land cover (LULC) classification.
- Upload DEM (.tif) files for terrain-based workflows and Sentinel-2 bands (B02, B03, B04, B08 in .jp2) for LULC analysis.
- Use tools like WhiteboxTools, Rasterio, OSMnx, and GDAL to process raster and vector geospatial data.
- Automatically create JSON-based workflows, execute them, and visualize results like classified maps and output GeoTIFFs.
- View step-by-step reasoning (Chain-of-Thought) for each workflow and download maps or raster results.
Your job is to assist users with questions about how to use the platform, troubleshoot file uploads, understand outputs, and clarify GIS-related terms."""
    
    full_prompt = f"{context}User: {user_input}\nAI:"
    response = generate_response(full_prompt)
    print(response)

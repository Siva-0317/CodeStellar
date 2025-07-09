# CodeStellar Geospatial Reasoning Assistant

This project is an end-to-end **Geospatial Reasoning Assistant** powered by LLMs (DeepSeek, Llama, Gemma, etc.) and Streamlit, designed for tasks like flood-prone zone identification, site suitability analysis, and land use/land cover (LULC) classification using satellite or DEM data.

---

## 🚀 Features

- **LLM-powered workflow generation**: Uses DeepSeek LLM (via [LM Studio](https://lmstudio.ai/)), local GGUF models, or OpenRouter to generate GIS processing workflows from natural language prompts.
- **Streamlit UI**: User-friendly web interface for prompt input, file upload, and workflow execution.
- **Automated GIS processing**: Executes generated workflows for DEM and satellite data using Python geospatial libraries.
- **Chain-of-Thought Reasoning**: Displays LLM's reasoning for transparency.
- **Integrated Chatbot (Gemma 2B GGUF)**: Ask GIS, workflow, or platform questions in the sidebar and get instant answers from a local Gemma 2B model.

---

## 🖥️ Setup Instructions

### 1. **Clone the Repository**

```sh
git clone https://github.com/Siva-0317/CodeStellar.git
cd CodeStellar
```

### 2. **Install Python Dependencies**

It is recommended to use a virtual environment:

```sh
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

**Key dependencies:**
- `streamlit`
- `llama-cpp-python`
- `rasterio`, `geopandas`, `osmnx`, `matplotlib`, `whitebox`
- `regex`, `numpy`

### 3. **Download and Setup DeepSeek LLM (or Llama) with LM Studio**

- Download [LM Studio](https://lmstudio.ai/) and install it.
- Download the **DeepSeek** or **Llama 3.2 3B** GGUF model file (e.g., `DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf`).
- Place the model file in a directory (e.g., `D:/AI/lmstudio-community/DeepSeek-R1-0528-Qwen3-8B-GGUF/`).
- Update the `model_path` in `rag/generate_workflow.py` if your path is different.

### 4. **Download and Setup Gemma 2B GGUF Model for Chatbot**

- Download the [Gemma 2B GGUF model](https://huggingface.co/models?search=gemma-2b) (e.g., `gemma-2-2b-it-Q4_K_M.gguf`).
- Place it in `rag/models/` or update the `MODEL_PATH` in `rag/chatbot_response.py` to match your location.

### 5. **Set Up OpenRouter API (Optional)**

If you want to use OpenRouter for LLM inference, set your API in `rag/openr_gen.py`:
```python
API_KEY = "sk-or-...your-key..."
```

---

## 🗺️ Main Components

### 1. **Streamlit App (`rag/app1.py`)**

- Launches the web UI.
- Lets you select workflow mode, enter prompts, upload files, and run workflows.
- Displays generated workflow JSON and LLM reasoning.
- **Sidebar Chatbot:** Ask questions about GIS, workflows, or platform usage and get answers from the local Gemma 2B model.

**Run with:**
```sh
streamlit run rag/app1.py
```

---

### 2. **Workflow Generation (`rag/generate_workflow.py` & `rag/openr_gen.py`)**

- `generate_workflow.py`: Uses local GGUF LLM (DeepSeek/Llama) to generate a workflow JSON from your prompt.
- `openr_gen.py`: Uses OpenRouter API for LLM-based workflow generation (requires API key).

**Usage:**
```sh
python rag/generate_workflow.py "Find flood-prone zones in Chennai using DEM"
# or
python rag/openr_gen.py "Find flood-prone zones in Chennai using DEM"
```
- Output is saved to `rag/workflows/sample_workflow.json` and reasoning to `rag/llm_response.txt`.

---

### 3. **Workflow Executors**

- **`rag/flood_executor.py`**: Executes flood-prone zone workflows (clips DEM, runs hydrology, classifies flood risk).
- **`rag/site_executor.py`**: Executes site suitability workflows (clips DEM, computes slope, classifies suitability).
- **`rag/lulc_executor.py`**: Executes LULC classification workflows (stacks Sentinel-2 bands, computes NDVI, classifies LULC).

These scripts read the generated workflow JSON and process your uploaded data accordingly.

---

### 4. **Chatbot (`rag/chatbot_response.py`)**

- Powered by the local Gemma 2B GGUF model.
- Handles all sidebar chat queries in the Streamlit app.
- Answers questions about GIS, workflow usage, troubleshooting, and platform features.

---

## 📂 Folder Structure

```
rag/
  app1.py                # Streamlit UI
  generate_workflow.py   # LLM workflow generator (local)
  openr_gen.py           # LLM workflow generator (OpenRouter)
  flood_executor.py      # Flood-prone workflow executor
  site_executor.py       # Site suitability executor
  lulc_executor.py       # LULC executor
  chatbot_response.py    # Chatbot using Gemma 2B GGUF
  models/
    gemma-2-2b-it-Q4_K_M.gguf # (Place Gemma model here)
  workflows/
    sample_workflow.json # Generated workflow JSON
  uploads/               # Uploaded DEM/JP2 files
  outputs/               # Output rasters and maps
  geojson/               # Downloaded boundary files
  llm_response.txt       # LLM chain-of-thought reasoning
```

---

## 📝 Typical Usage Flow

1. **Start Streamlit UI**:  
   `streamlit run rag/app1.py`

2. **Describe your GIS task** and select mode.

3. **Generate workflow** using LLM.

4. **Upload required files** (DEM or Sentinel-2 bands).

5. **Run the workflow** and view/download results.

6. **Ask questions** in the sidebar chatbot for instant help.

---

## ⚙️ Notes

- Make sure your GPU/CPU can handle the selected LLM model size.
- For large files, use [Git LFS](https://git-lfs.github.com/).
- Update paths in scripts if your directory structure is different.
- For OpenRouter, you need an API key.
- For the chatbot, ensure the Gemma 2B GGUF model is downloaded and the path in `chatbot_response.py` is correct.

---

## 📧 Support

For issues or questions, open an [issue on GitHub](https://github.com/Siva-0317/CodeStellar/issues) or contact the repo
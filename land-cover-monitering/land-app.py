import streamlit as st
import json
from pathlib import Path
import rasterio
import matplotlib.pyplot as plt
import numpy as np
import subprocess

# Paths
prompt_path = Path("llm/prompts/input.txt")
template_path = Path("llm/cot_templates/landcover_cot.txt")
workflow_path = Path("llm/workflows/workflow1.json")
ndvi_path = Path("data/processed/ndvi.tif")
classified_path = Path("data/processed/land_cover_classified.tif")

st.set_page_config(page_title="Land Cover Monitoring Assistant", layout="wide")
st.title("🛰️ Land Cover Monitoring Assistant")
st.markdown("🔗 *ISRO BAH 2025 – Chain-of-Thought LLM System*")

# 1. Prompt Input
with st.expander("✏️ Step 1: Edit Natural Language Prompt"):
    prompt = prompt_path.read_text()
    user_input = st.text_area("Prompt", value=prompt, height=150)
    if st.button("💾 Save Prompt"):
        prompt_path.write_text(user_input)
        st.success("Prompt saved!")

# 2. Generate Workflow
def simulate_llm_response(prompt, template):
    st.info("Generating workflow based on prompt...")
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
    return workflow

if st.button("🧠 Generate Workflow"):
    template = template_path.read_text()
    workflow = simulate_llm_response(user_input, template)
    workflow_path.write_text(json.dumps(workflow, indent=4))
    st.success("✅ Workflow generated and saved!")

# 3. Display Workflow JSON
if workflow_path.exists():
    with st.expander("📦 View Generated Workflow (JSON)"):
        st.code(workflow_path.read_text(), language="json")

# 4. Execute Workflow
if st.button("🚀 Execute Workflow"):
    result = subprocess.run(
        ["python", "llm/execute_workflow.py", str(workflow_path)],
        capture_output=True, text=True
    )
    st.text_area("Execution Log", result.stdout + result.stderr, height=300)
    if "✅ Land cover classified" in result.stdout:
        st.success("🎉 Workflow executed successfully!")

# 5. Visualize Final Map
if classified_path.exists():
    with st.expander("🗺️ Visualize Classified Land Cover Map"):
        with rasterio.open(classified_path) as src:
            image = src.read(1)
        cmap = plt.cm.get_cmap("Set1", 5)  # contrasting
        fig, ax = plt.subplots(figsize=(10, 8))
        cax = ax.imshow(image, cmap=cmap)
        cbar = plt.colorbar(cax, ax=ax, ticks=[1, 2, 3, 4])
        cbar.ax.set_yticklabels(['Water', 'Barren', 'Urban', 'Forest'])
        st.pyplot(fig)

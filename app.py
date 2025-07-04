# ✅ Updated app.py for Flood-Prone Zone Workflow

import streamlit as st
import os
import subprocess
import json
import shutil
from datetime import datetime
import sys
from PIL import Image

# Set folders
UPLOAD_FOLDER = "rag/uploads"
OUTPUT_FOLDER = "rag"

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# UI Setup
st.set_page_config(page_title="Flood Risk Zone GIS Assistant", layout="wide")
st.title("🌊 Flood-Prone Zone Identification using DEM")

# 1. Prompt input
st.header("Step 1: Enter your geospatial task prompt")
prompt = st.text_area("Describe your GIS task:", placeholder="e.g., Find flood-prone zones in Chennai using a DEM")

if st.button("Generate Flood Workflow JSON using LLM"):
    with st.spinner("Generating workflow using LLM..."):
        result = subprocess.run([
            sys.executable, "rag/generate_workflow.py", prompt
        ], capture_output=True, text=True)

        if result.returncode == 0:
            st.success("✅ sample_workflow.json generated.")
            with open("rag/workflows/sample_workflow.json") as f:
                workflow = json.load(f)
            st.json(workflow)
        else:
            st.error("❌ Failed to generate workflow.")
            st.text(result.stderr)

# 2. Upload TIF file
st.header("Step 2: Upload your DEM (.tif) file")
tif_file = st.file_uploader("Upload a DEM GeoTIFF file", type=["tif"])

if tif_file:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uploaded_path = os.path.join(UPLOAD_FOLDER, f"input_{timestamp}.tif")
    with open(uploaded_path, "wb") as f:
        f.write(tif_file.read())
    st.success(f"Uploaded: {uploaded_path}")

    # Update sample_workflow.json with uploaded file
    with open("rag/workflows/sample_workflow.json") as f:
        workflow = json.load(f)
    for step in workflow.get("workflow", []):
        if "args" in step and "input_file" in step["args"]:
            step["args"]["input_file"] = uploaded_path
    with open("rag/workflows/sample_workflow.json", "w") as f:
        json.dump(workflow, f, indent=2)
    st.info("🔁 Updated workflow to use uploaded file.")

    # 3. Execute workflow
    if st.button("Run Flood Analysis Workflow"):
        with st.spinner("Running workflow_executor.py..."):
            result = subprocess.run([sys.executable, "rag/workflow_executor.py"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Workflow executed successfully!")
                st.text(result.stdout)

                # Display output raster and map
                st.header("🗺️ Flood Risk Map")
                image_path = os.path.join("rag", "flood_risk_map.png")
                if os.path.exists(image_path):
                    st.image(image_path, caption="Flood Risk Zones", use_column_width=True)
                else:
                    st.warning("⚠️ No flood risk map image generated.")

                # List output rasters
                st.header("📊 Output Raster Files")
                for file in os.listdir("rag"):
                    if file.endswith(".tif"):
                        st.markdown(f"**{file}**")
            else:
                st.error("❌ Workflow execution failed.")
                st.text(result.stderr)

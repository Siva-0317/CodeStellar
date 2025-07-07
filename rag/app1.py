import streamlit as st
import os
import subprocess
import json
from datetime import datetime
import sys

# Set folders
UPLOAD_FOLDER = "rag/uploads"
WORKFLOW_FOLDER = "rag/workflows"
OUTPUT_FOLDER = "rag/outputs"

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(WORKFLOW_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

st.set_page_config(page_title="Geospatial Reasoning Assistant", layout="wide")
st.title("🌍 Geospatial Reasoning Assistant")

# --- Mode Selector ---
mode = st.radio("Choose Workflow Mode:", ["Flood-Prone Zone Identification", "Site Suitability Analysis"])

# --- Prompt Input ---
st.header("Step 1: Describe your GIS task")
default_prompt = (
    "Find flood-prone zones in Chennai"
    if mode == "Flood-Prone Zone Identification"
    else "Find suitable sites for building in Vellore"
)
prompt = st.text_area("Enter task prompt:", placeholder=f"e.g., {default_prompt}")

workflow_script = "rag/openr_gen.py"
executor_script = "rag/workflow_executor.py" if mode == "Flood-Prone Zone Identification" else "rag/workflow_exe2.py"

if st.button("Generate Workflow JSON using LLM"):
    with st.spinner("🔧 Generating workflow from LLM..."):
        result = subprocess.run([sys.executable, workflow_script, prompt], capture_output=True, text=True)

        if result.returncode == 0:
            st.success("✅ Workflow JSON generated.")
            with open("rag/workflows/sample_workflow.json") as f:
                workflow = json.load(f)
            st.json(workflow)
        else:
            st.error("❌ Workflow generation failed.")
            st.text(result.stderr)

# --- GeoJSON Location Input ---
if mode in ["Site Suitability Analysis", "Flood-Prone Zone Identification"]:
    st.header("Step 2: Enter Location for GeoJSON Boundary")
    location_input = st.text_input("Enter location name (e.g., Vellore or Goa):")
    if location_input:
        with open("rag/workflows/sample_workflow.json") as f:
            workflow = json.load(f)
        for step in workflow.get("workflow", []):
            if "task" in step:
                if mode == "Site Suitability Analysis":
                    step["task"] = f"site suitability for {location_input}"
                elif mode == "Flood-Prone Zone Identification":
                    step["task"] = f"flood-prone analysis for {location_input}"
        with open("rag/workflows/sample_workflow.json", "w") as f:
            json.dump(workflow, f, indent=2)
        st.success(f"📍 Location updated in workflow: {location_input}")

# --- Upload TIF File ---
st.header("Step 3: Upload your DEM (.tif) file")
tif_file = st.file_uploader("Upload a DEM GeoTIFF file", type=["tif", "tiff"])

if tif_file:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uploaded_path = os.path.join(UPLOAD_FOLDER, f"input_{timestamp}.tif")
    with open(uploaded_path, "wb") as f:
        f.write(tif_file.read())
    st.success(f"Uploaded: {uploaded_path}")

    # Update workflow with uploaded file path
    with open("rag/workflows/sample_workflow.json") as f:
        workflow = json.load(f)
    for step in workflow.get("workflow", []):
        if "args" in step and "input_file" in step["args"]:
            step["args"]["input_file"] = uploaded_path
    with open("rag/workflows/sample_workflow.json", "w") as f:
        json.dump(workflow, f, indent=2)
    st.info("🔁 Updated workflow to use uploaded file.")

    # --- Execute Workflow ---
    if st.button("Run Workflow"):
        with st.spinner("⏳ Executing Workflow..."):
            result = subprocess.run([sys.executable, executor_script], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Workflow executed successfully!")
                st.text(result.stdout)

                # Output Map Image
                st.header("🗺️ Output Map")
                map_img = (
                    os.path.join("rag","outputs" ,"flood_risk_map.png")
                    if mode == "Flood-Prone Zone Identification"
                    else os.path.join("rag", "outputs", "site_suitability_map.png")
                )
                if os.path.exists(map_img):
                    st.image(map_img, caption=os.path.basename(map_img).replace("_", " ").title(), use_container_width=True)
                    with open(map_img, "rb") as f:
                        st.download_button("📥 Download Map Image", f, file_name=os.path.basename(map_img))
                else:
                    st.warning("⚠️ Map image not generated.")

                # Output Raster Files
                st.header("📊 Output Raster Files")
                for file in os.listdir(OUTPUT_FOLDER):
                    if file.endswith(".tif"):
                        st.markdown(f"📄 {file}")

                # Display JSON Workflow
                with open("rag/workflows/sample_workflow.json") as f:
                    st.header("🧠 Executed JSON Workflow")
                    st.json(json.load(f))
            else:
                st.error("❌ Workflow execution failed.")
                st.text(result.stderr)

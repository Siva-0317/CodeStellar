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
mode = st.radio("Choose Workflow Mode:", ["Flood-Prone Zone Identification", "Site Suitability Analysis", "Land Cover Classification (LULC)"])

# --- Prompt Input ---
st.header("Step 1: Describe your GIS task")
def_prompt = {
    "Flood-Prone Zone Identification": "Find flood-prone zones in Chennai",
    "Site Suitability Analysis": "Find suitable sites for building in Vellore",
    "Land Cover Classification (LULC)": "Classify land cover from Sentinel-2 bands in Chennai"
}
prompt = st.text_area("Enter task prompt:", placeholder=f"e.g., {def_prompt[mode]}")

workflow_script = "rag/openr_gen.py"
executor_script = {
    "Flood-Prone Zone Identification": "rag/flood_executor.py",
    "Site Suitability Analysis": "rag/site_executor.py",
    "Land Cover Classification (LULC)": "rag/lulc_executor.py"
}[mode]

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

# --- Upload File(s) ---
if mode == "Land Cover Classification (LULC)":
    st.header("Step 3: Upload Sentinel-2 JP2 Bands")
    uploaded_files = st.file_uploader("Upload 4 Sentinel-2 bands (B02, B03, B04, B08)", type=["jp2"], accept_multiple_files=True)

    if uploaded_files and len(uploaded_files) == 4:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        band_map = {}
        for file in uploaded_files:
            fname = file.name
            if "B02" in fname:
                band_map["B02"] = fname
            elif "B03" in fname:
                band_map["B03"] = fname
            elif "B04" in fname:
                band_map["B04"] = fname
            elif "B08" in fname:
                band_map["B08"] = fname

            save_path = os.path.join(UPLOAD_FOLDER, fname)
            with open(save_path, "wb") as f:
                f.write(file.read())

        if len(band_map) == 4:
            st.success("✅ All required bands uploaded.")
            if st.button("Run Workflow"):
                with st.spinner("⏳ Executing LULC Workflow..."):
                    result = subprocess.run([sys.executable, executor_script], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ Workflow executed successfully!")
                        st.text(result.stdout)

                        st.header("🗺️ LULC Output Map")
                        lulc_img = os.path.join("rag", "outputs", "lulc_map.png")
                        if os.path.exists(lulc_img):
                            st.image(lulc_img, caption="Land Cover Map", use_container_width=True)
                            with open(lulc_img, "rb") as f:
                                st.download_button("📥 Download Map Image", f, file_name="lulc_map.png")
                        else:
                            st.warning("⚠️ LULC map not found.")

                        st.header("📊 Output Raster Files")
                        for file in os.listdir(OUTPUT_FOLDER):
                            if file.endswith(".tif"):
                                st.markdown(f"📄 {file}")
                    else:
                        st.error("❌ LULC Workflow execution failed.")
                        st.text(result.stderr)
        else:
            st.warning("⚠️ Please upload all 4 required bands (B02, B03, B04, B08).")

else:
    # --- Upload TIF File for Flood/Site ---
    st.header("Step 3: Upload your DEM (.tif) file")
    tif_file = st.file_uploader("Upload a DEM GeoTIFF file", type=["tif", "tiff"])

    if tif_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        uploaded_path = os.path.join(UPLOAD_FOLDER, f"input_{timestamp}.tif")
        with open(uploaded_path, "wb") as f:
            f.write(tif_file.read())
        st.success(f"Uploaded: {uploaded_path}")

        with open("rag/workflows/sample_workflow.json") as f:
            workflow = json.load(f)
        for step in workflow.get("workflow", []):
            if "args" in step and "input_file" in step["args"]:
                step["args"]["input_file"] = uploaded_path
        with open("rag/workflows/sample_workflow.json", "w") as f:
            json.dump(workflow, f, indent=2)
        st.info("🔁 Updated workflow to use uploaded file.")

        if st.button("Run Workflow"):
            with st.spinner("⏳ Executing Workflow..."):
                result = subprocess.run([sys.executable, executor_script], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Workflow executed successfully!")
                    st.text(result.stdout)

                    st.header("🗺️ Output Map")
                    map_img = (
                        os.path.join("rag", "outputs", "flood_risk_map.png")
                        if mode == "Flood-Prone Zone Identification"
                        else os.path.join("rag", "outputs", "site_suitability_map.png")
                    )
                    if os.path.exists(map_img):
                        st.image(map_img, caption=os.path.basename(map_img).replace("_", " ").title(), use_container_width=True)
                        with open(map_img, "rb") as f:
                            st.download_button("📥 Download Map Image", f, file_name=os.path.basename(map_img))
                    else:
                        st.warning("⚠️ Map image not generated.")

                    st.header("📊 Output Raster Files")
                    for file in os.listdir(OUTPUT_FOLDER):
                        if file.endswith(".tif"):
                            st.markdown(f"📄 {file}")

                    with open("rag/workflows/sample_workflow.json") as f:
                        st.header("🧠 Executed JSON Workflow")
                        st.json(json.load(f))
                else:
                    st.error("❌ Workflow execution failed.")
                    st.text(result.stderr)

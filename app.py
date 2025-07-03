import streamlit as st
import os
import subprocess
import json
import shutil
from datetime import datetime

# Set folders
UPLOAD_FOLDER = "rag/uploads"
OUTPUT_FOLDER = "rag/outputs"

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# UI Setup
st.set_page_config(page_title="GeoAI CoT GIS System", layout="wide")
st.title("🧠📍 Chain-of-Thought GIS Workflow Assistant")

# 1. Prompt input
st.header("Step 1: Enter your geospatial analysis prompt")
prompt = st.text_area("Describe your GIS task:", placeholder="e.g., Find flood-prone zones in Chennai using a DEM")

if st.button("Generate Workflow JSON using Mistral"):
    with st.spinner("Generating workflow using Mistral LLM..."):
        result = subprocess.run([
            "python", "rag/generate_workflow.py", prompt
        ], capture_output=True, text=True)

        if result.returncode == 0:
            st.success("✅ sample_workflow.json generated.")
            with open("rag/workflows/sample_workflow.json") as f:
                workflow = json.load(f)
            st.json(workflow)
        else:
            st.error("❌ Failed to generate workflow.")
            st.text(result.stderr)

# 2. Run explanation script
if os.path.exists("rag/sample_workflow.json"):
    if st.button("Explain Workflow Steps"):
        with st.spinner("Explaining workflow steps..."):
            result = subprocess.run(["python", "rag/explain_workflow.py"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ step_explanations.json generated.")
                with open("rag/workflows/step_explanations.json") as f:
                    explanation = json.load(f)
                st.json(explanation)
            else:
                st.error("❌ Failed to explain steps.")
                st.text(result.stderr)

# 3. Upload TIF file
st.header("Step 3: Upload your GeoTIFF (.tif) file")
tif_file = st.file_uploader("Upload a DEM or other raster file", type=["tif"])

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
        if "input_file" in step["args"]:
            step["args"]["input_file"] = uploaded_path
    with open("rag/workflows/sample_workflow.json", "w") as f:
        json.dump(workflow, f, indent=2)
    st.info("🔁 Updated workflow to use uploaded file.")

    # 4. Execute workflow
    if st.button("Run GIS Workflow"):
        with st.spinner("Running workflow_executor.py..."):
            result = subprocess.run(["python", "workflow_executor.py"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Workflow executed successfully!")
                st.text(result.stdout)

                # Show output files
                st.header("📊 Output Rasters")
                for file in os.listdir(OUTPUT_FOLDER):
                    if file.endswith(".tif"):
                        st.markdown(f"**{file}**")
                        st.image(os.path.join(OUTPUT_FOLDER, file), caption=file)
            else:
                st.error("❌ Workflow execution failed.")
                st.text(result.stderr)

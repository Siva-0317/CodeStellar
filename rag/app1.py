import streamlit as st
import os
import subprocess
import json
from datetime import datetime
import sys
from llama_cpp import Llama

# Set folders
UPLOAD_FOLDER = "rag/uploads"
WORKFLOW_FOLDER = "rag/workflows"
OUTPUT_FOLDER = "rag/outputs"
COT_FILE = "rag/llm_response.txt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(WORKFLOW_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

st.set_page_config(page_title="Geospatial Reasoning Assistant", layout="wide")
st.title("🌍 Geospatial Reasoning Assistant")

# Initialize session state
if "prompt_history" not in st.session_state:
    st.session_state.prompt_history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Mode Selector ---
mode = st.radio("Choose Workflow Mode:", [
    "Flood-Prone Zone Identification",
    "Site Suitability Analysis",
    "Land Use / Land Cover (LULC) Classification"
])

# --- Prompt Input ---
st.header("Step 1: Describe your GIS task")
def_prompt_map = {
    "Flood-Prone Zone Identification": "Find flood-prone zones in Chennai",
    "Site Suitability Analysis": "Find suitable sites for building in Vellore",
    "Land Use / Land Cover (LULC) Classification": "Classify land cover from Sentinel 2 for Coimbatore"
}
prompt = st.text_area("Enter task prompt:", placeholder=f"e.g., {def_prompt_map[mode]}")

workflow_script = "rag/generate_workflow.py"
executor_script = {
    "Flood-Prone Zone Identification": "rag/flood_executor.py",
    "Site Suitability Analysis": "rag/site_executor.py",
    "Land Use / Land Cover (LULC) Classification": "rag/lulc_executor.py"
}[mode]

# --- Generate Workflow JSON ---
if st.button("Generate Workflow JSON using LLM"):
    with st.spinner("🔧 Generating workflow from LLM..."):
        result = subprocess.run([sys.executable, workflow_script, prompt], capture_output=True, text=True)

        if result.returncode == 0:
            st.success("✅ Workflow JSON generated.")
            st.session_state.prompt_history.append(prompt)

            with open("rag/workflows/sample_workflow.json") as f:
                workflow = json.load(f)
            st.json(workflow)

            if os.path.exists(COT_FILE):
                with open(COT_FILE, "r", encoding="utf-8") as f:
                    cot_text = f.read()
                st.header("🧠 Chain-of-Thought Reasoning")
                st.code(cot_text, language="markdown")

        else:
            st.error("❌ Workflow generation failed.")
            st.text(result.stderr)

# --- Prompt History Sidebar ---
if st.session_state.prompt_history:
    st.sidebar.header("📜 Prompt History")
    for idx, p in enumerate(reversed(st.session_state.prompt_history), 1):
        st.sidebar.markdown(f"**{idx}.** {p}")

# --- Chatbot Sidebar Assistant ---
st.sidebar.title("💬 Assistant Chatbot")
user_input = st.sidebar.text_input("Ask me anything:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if user_input:
    # Prepare conversation context
    context = "\n".join([f"User: {q}\nAI: {a}" for q, a in st.session_state.chat_history])
    combined_prompt = f"{context}\nUser: {user_input}"

    # Call external chatbot script
    chatbot_script = "rag/chatbot_response.py"
    result = subprocess.run(
        [sys.executable, chatbot_script, combined_prompt],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        response = result.stdout.strip()
        st.session_state.chat_history.append((user_input, response))
    else:
        response = "⚠️ Failed to generate response."
        st.error(result.stderr)

# Display previous messages
for q, a in reversed(st.session_state.chat_history):
    st.sidebar.markdown(f"**You:** {q}")
    st.sidebar.markdown(f"**Assistant:** {a}")


# --- Location Input for DEM Tasks ---
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

# --- Upload JP2 for LULC ---
if mode == "Land Use / Land Cover (LULC) Classification":
    st.header("Step 3: Upload Sentinel-2 Bands (JP2 format)")
    uploaded_files = st.file_uploader("Upload bands B02, B03, B04, B08", type=["jp2"], accept_multiple_files=True)

    band_map = {"B02": None, "B03": None, "B04": None, "B08": None}
    for file in uploaded_files:
        for band in band_map:
            if band in file.name:
                save_path = os.path.join(UPLOAD_FOLDER, file.name)
                with open(save_path, "wb") as f:
                    f.write(file.read())
                band_map[band] = save_path

    if all(band_map.values()):
        st.success("✅ All required bands uploaded.")
        if st.button("Run Workflow"):
            with st.spinner("⏳ Executing Workflow..."):
                result = subprocess.run([sys.executable, executor_script], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Workflow executed successfully!")
                    st.text(result.stdout)

                    st.header("🗺️ Output Map")
                    map_img = os.path.join("rag", "outputs", "lulc_map.png")
                    if os.path.exists(map_img):
                        st.image(map_img, caption="LULC Classification", use_container_width=True)
                        with open(map_img, "rb") as f:
                            st.download_button("📥 Download Map Image", f, file_name="lulc_map.png")

                    st.header("📊 Output Raster Files")
                    for file in os.listdir(OUTPUT_FOLDER):
                        if file.endswith(".tif"):
                            st.markdown(f"📄 {file}")

                    if os.path.exists(COT_FILE):
                        with open(COT_FILE, "r", encoding="utf-8") as f:
                            cot_text = f.read()
                        st.header("🧠 Chain-of-Thought Reasoning")
                        st.code(cot_text, language="markdown")
                else:
                    st.error("❌ Workflow execution failed.")
                    st.text(result.stderr)
    else:
        st.warning("Please upload all required bands.")

# --- Upload DEM for Flood/Suitability ---
else:
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

                    if os.path.exists(COT_FILE):
                        with open(COT_FILE, "r", encoding="utf-8") as f:
                            cot_text = f.read()
                        st.header("🧠 Chain-of-Thought Reasoning")
                        st.code(cot_text, language="markdown")
                else:
                    st.error("❌ Workflow execution failed.")
                    st.text(result.stderr)

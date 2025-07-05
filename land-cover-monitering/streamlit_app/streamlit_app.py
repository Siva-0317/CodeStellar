# ui/streamlit_app.py

import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="GeoCoT: LLM Geospatial Reasoner", layout="wide")

st.title("🗺️ Chain-of-Thought Geospatial Assistant")
st.markdown("This tool allows you to enter a natural language query and generates a geospatial workflow using Chain-of-Thought reasoning.")

# Input query
query = st.text_input("🌍 Enter your geospatial query (e.g., 'Find flood risk zones in Chennai')")

# Submit button
if st.button("Generate Workflow"):
    with st.spinner("🧠 Thinking with Chain-of-Thought reasoning..."):
        # Simulated CoT reasoning (we'll replace with real LLM later)
        fake_reasoning = [
            "1. Identify spatial extent: Chennai boundary",
            "2. Fetch flood-prone areas from OSM/Bhoonidhi",
            "3. Overlay DEM to extract elevation",
            "4. Buffer critical areas and compute risk zones",
        ]
        fake_workflow = {
            "task": query,
            "steps": ["load_boundary", "fetch_flood_data", "load_DEM", "compute_overlay", "generate_risk_map"]
        }

        st.subheader("🧾 Chain-of-Thought Reasoning")
        for step in fake_reasoning:
            st.markdown(f"- {step}")

        st.subheader("⚙️ JSON Workflow Output")
        st.code(json.dumps(fake_workflow, indent=2), language="json")

        # Save output to workflows/definitions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../workflows/definitions/workflow_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(fake_workflow, f, indent=2)
        st.success(f"Workflow saved as {filename}")

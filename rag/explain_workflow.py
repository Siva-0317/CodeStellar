# rag/explain_workflow.py
"""import json
from retriever import query_docs

def explain_workflow(json_path):
    with open(json_path) as f:
        data = json.load(f)

    tools = set(step["tool"] for step in data["steps"])

    explanations = {}
    for tool in tools:
        chunks = query_docs(tool)
        explanations[tool] = chunks[0] if chunks else "No info found."

    return explanations

if __name__ == "__main__":
    results = explain_workflow("rag/sample_workflow.json")
    for tool, explanation in results.items():
        print(f"\n🔧 {tool.upper()}:\n{explanation}")"""

#Updated explain_workflow.py
import json
import os
from retriever import query_docs

def explain_workflow(json_path):
    with open(json_path) as f:
        data = json.load(f)

    steps = data["workflow"]
    tool_names = set()

    for step in steps:
        tool = step.get("args", {}).get("tool", "")
        if tool:
            tool_names.add(tool)

        action = step.get("action", "").lower()
        if "whiteboxtools" in action:
            tool_names.add("WhiteboxTools")
        elif "qgis" in action:
            tool_names.add("QGIS")
        elif "gdal" in action:
            tool_names.add("GDAL")
        elif "kriging" in action:
            tool_names.add("Kriging")
        elif "idw" in action:
            tool_names.add("IDW")

    explanations = {}
    for tool in tool_names:
        chunks = query_docs(tool)
        explanations[tool] = chunks[0] if chunks else "No explanation found."

    # ✅ Force save in current script's directory
    output_path = os.path.join(os.path.dirname(__file__), "step_explanations.json")
    with open(output_path, "w") as f:
        json.dump(explanations, f, indent=4)

    print(f"✅ Step explanations saved to: {output_path}")
    return explanations

if __name__ == "__main__":
    explain_workflow("rag/sample_workflow.json")



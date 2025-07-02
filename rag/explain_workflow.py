# rag/explain_workflow.py
import json
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
    results = explain_workflow("sample_workflow.json")
    for tool, explanation in results.items():
        print(f"\n🔧 {tool.upper()}:\n{explanation}")

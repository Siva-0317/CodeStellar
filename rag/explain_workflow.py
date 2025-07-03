import json
from retriever import retrieve_explanation

def explain_workflow(json_path="rag/workflows/sample_workflow.json"):
    with open(json_path, "r") as f:
        workflow = json.load(f)["workflow"]

    explanations = []

    for step in workflow:
        query = f"What does this GIS step do? Tool: {step['args']['tool']}, Action: {step['action']}"
        docs = retrieve_explanation(query)
        explanations.append({
            "step": step,
            "explanation": docs[0].page_content if docs else "No explanation found."
        })

    with open("rag/workflows/step_explanations.json", "w") as f:
        json.dump(explanations, f, indent=4)

    return explanations

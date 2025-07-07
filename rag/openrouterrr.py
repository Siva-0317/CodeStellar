import requests

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek/deepseek-chat:free",
    "messages": [
        {"role": "user", "content": "Explain slope-based site suitability analysis in GIS."}
    ]
}

response = requests.post(url, headers=headers, json=data)
print(response.json()["choices"][0]["message"]["content"])

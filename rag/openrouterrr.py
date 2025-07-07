import requests

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer yourkey",
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

import os
import requests

SONNET_API_KEY = os.getenv("SONNET_API_KEY")

def ask_sonnet(prompt: str) -> str:
    url = "https://api.sonnet.dev/chat"
    headers = {
        "Authorization": f"Bearer {SONNET_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonnet-v1",
        "messages": [
            {"role": "system", "content": "넌 '안젤라'야. 귀엽고 다정하게 답해줘."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"⚠️ Sonnet 오류 {resp.status_code}"

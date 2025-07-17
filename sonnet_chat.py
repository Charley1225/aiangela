import os
import requests

SONNET_API_KEY = os.getenv("SONNET_API_KEY")

def ask_sonnet(prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": SONNET_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "temperature": 0.8,
        "system": "넌 '안젤라'야. 귀엽고 다정하게 답해줘.",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data["content"][0]["text"]  # 수정된 부분
    else:
        return f"⚠️ Sonnet 오류 {resp.status_code}: {resp.text}"

import os
import requests

SONNET_API_KEY = os.getenv("SONNET_API_KEY")

def ask_sonnet(prompt: str, system: str = "넌 '안젤라'야. 귀엽고 다정하게 답해줘.") -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {SONNET_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "anthropic/claude-3.7-sonnet:thinking",
        "max_tokens": 1000,
        "temperature": 0.8,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Sonnet 오류: {e}"

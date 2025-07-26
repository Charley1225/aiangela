import os
import requests

SONNET_API_KEY = os.getenv("SONNET_API_KEY")

def ask_sonnet(prompt: str, system: str = None) -> str:
    if system is None:
        raise ValueError("⚠️ system prompt가 누락되었습니다.")
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
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"⚠️ Sonnet 오류: {e}"

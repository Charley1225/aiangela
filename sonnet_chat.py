import os
import requests

SONNET_API_KEY = os.getenv("SONNET_API_KEY")

def ask_sonnet(prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"  # 최신 Anthropic API 엔드포인트
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": SONNET_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": "claude-sonnet-4-20250514",  # 최신 소네트 4 모델명
        "max_tokens": 1000,
        "stream": False,                      # 스트리밍 안할 거면 False
        "messages": [
            {"role": "system", "content": "넌 '안젤라'야. 귀엽고 다정하게 답해줘."},
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        # 응답 포맷이 Anthropic 기준이라 key 위치가 다를 수 있음
        # 예시로 choices[0].message.content 사용
        return resp.json()["choices"][0]["message"]["content"]
    return f"⚠️ Sonnet 오류 {resp.status_code}"

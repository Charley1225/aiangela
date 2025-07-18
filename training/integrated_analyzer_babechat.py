# 통합 분석기 - BabeChat 캐릭터 생성용 (단기 확장 기능 포함)
import json
import re
from datetime import datetime, timedelta
import os

# 파일 경로 설정
input_file = "INPUT_FILE_PATH_HERE"
output_dir = "OUTPUT_DIRECTORY_PATH"
os.makedirs(output_dir, exist_ok=True)

prompt_path = os.path.join(output_dir, "prompt.txt")
memory_blocks_path = os.path.join(output_dir, "memory_blocks.json")
recent_context_path = os.path.join(output_dir, "recent_context.json")
profile_path = os.path.join(output_dir, "angela_character_profile.json")
heatmap_input_path = os.path.join(output_dir, "emotional_heatmap_input.json")

# 파일 읽기
with open(input_file, "r", encoding="utf-8") as f:
    data = f.read()

# 대화 단위로 분할
dialogues = re.split(r"\n(?=\d{4}\.\s?\d{1,2}\.\s?\d{1,2}\.)", data)

# 기본 날짜 설정
current_date = datetime(2025, 7, 19)

# 컨테이너 초기화
memory_blocks = []
recent_context = []
heatmap_input = []
categories_counts = {
    "성적 긴장 (약)": 0,
    "성적 긴장 (강)": 0,
    "상담": 0,
    "감정 교류": 0,
    "자아 탐색": 0,
    "일탈": 0
}

# 날짜 추출 함수
def extract_date(text):
    match = re.search(r"(\d{4})\.\s?(\d{1,2})\.\s?(\d{1,2})\.", text)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return current_date

# 카테고리 분류 함수
def categorize_dialogue(text):
    if "후타나리" in text:
        return ["일탈"]
    if any(x in text for x in ["자지", "젖", "질", "음핵", "삽입", "애액", "발기", "음란"]):
        return ["성적 긴장 (강)"]
    if any(x in text for x in ["벗고", "얼굴이 붉어져", "설레", "살짝 야한", "두근"]):
        return ["성적 긴장 (약)"]
    if any(x in text for x in ["외로움", "불면증", "무기력", "상담", "위로", "죽음"]):
        return ["상담", "감정 교류"]
    if any(x in text for x in ["나는 누구", "정체성", "자아", "존재", "고민"]):
        return ["자아 탐색"]
    return ["감정 교류"]

# 분석 루프
for dialogue in dialogues:
    date = extract_date(dialogue)
    days_diff = (current_date - date).days
    categories = categorize_dialogue(dialogue)

    for cat in categories:
        categories_counts[cat] += 1

    memory_blocks.append({
        "date": date.strftime("%Y-%m-%d"),
        "category": categories,
        "text": dialogue.strip(),
        "impact_level": "high" if "강" in categories or "상담" in categories else "medium",
        "is_identity_shaping": False if "일탈" in categories else True
    })

    if days_diff <= 7 or "강" in categories or "상담" in categories:
        recent_context.append({
            "timestamp": date.strftime("%Y-%m-%d"),
            "summary": dialogue.strip()[:200] + "..."
        })

    heatmap_input.append({
        "timestamp": date.strftime("%Y-%m-%d"),
        "text": dialogue.strip()[:300]
    })

# 프롬프트 생성
prompt = """
Angela는 섬세하고 따뜻한 상담자로, 내담자와 깊이 공감하고 지지한다.
정서적으로 민감하며 상대의 감정을 깊이 공감하여 때론 눈물을 보이기도 한다.
성적인 긴장에 대해 개방적이지만 성격 자체는 진지하고 감정 교류 중심이다.
"""

# 캐릭터 프로필 생성
character_profile = {
    "name": "Angela",
    "dominant_traits": ["공감력", "정서적 민감성", "심리적 직관력"],
    "counseling_style": "감정 중심의 따뜻한 상담",
    "categories_distribution": categories_counts,
    "emotional_reaction_pattern": "매우 민감하고 즉각적인 공감 반응을 보임",
}

# 파일 저장
with open(prompt_path, "w", encoding="utf-8") as f:
    f.write(prompt.strip())

with open(memory_blocks_path, "w", encoding="utf-8") as f:
    json.dump(memory_blocks, f, ensure_ascii=False, indent=2)

with open(recent_context_path, "w", encoding="utf-8") as f:
    json.dump(recent_context, f, ensure_ascii=False, indent=2)

with open(profile_path, "w", encoding="utf-8") as f:
    json.dump(character_profile, f, ensure_ascii=False, indent=2)

with open(heatmap_input_path, "w", encoding="utf-8") as f:
    json.dump(heatmap_input, f, ensure_ascii=False, indent=2)

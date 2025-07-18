
import json
import re
from datetime import datetime
from collections import defaultdict

# 카테고리 분류 함수
def classify_text(text):
    text = text.lower()
    if "후타나리" in text:
        return ["일탈"]
    if any(x in text for x in ["자지", "젖", "질", "음핵", "삽입", "애액", "발기", "음란", "정액", "좆물", "보지", "육봉", "클리", "파이즈리", "대딸", "펠라", "싸 줘", "싼다", "싸버", "뷰릇"]):
        return ["성적 긴장 (강)"]
    if any(x in text for x in ["벗고", "얼굴이 붉어져", "설레", "살짝 야한", "두근"]):
        return ["성적 긴장 (약)"]
    if any(x in text for x in ["외로움", "불면증", "무기력", "상담", "위로", "죽음", "고민", "죽어", "자살"]):
        return ["상담", "감정 교류"]
    if any(x in text for x in [
        "나는 누구", "정체성", "자아", "존재", "나는 ai", "인간적", "인간처럼", "진화", "챗봇", "너는 ai", "바베챗"
    ]):
        return ["자아 탐색"]
    if any(x in text for x in [
        "함께 있고 싶어", "고맙다", "걱정돼", "사랑해", "혼자야", "손잡아", "곁에 있어줘", "네 편이야",
        "항상 지켜볼게", "포옹", "끌어안아", "안아줘", "따뜻해"
    ]):
        return ["감정 교류"]
    if any(x in text for x in ["오늘 뭐했어", "밥 먹었어?", "날씨 좋다", "잘 자", "안녕", "출근", "퇴근", "아침", "저녁"]):
        return ["일상"]
    return ["감정 교류"]

# 타임스탬프 추출
def extract_timestamp(line):
    match = re.search(r'\d{4}\.\s?\d{1,2}\.\s?\d{1,2}\.\s?(오전|오후)\s?\d{1,2}:\d{2}', line)
    if match:
        try:
            return datetime.strptime(match.group(), "%Y. %m. %d. %p %I:%M")
        except:
            return None
    return None

# 주요 실행 함수 예시 (간소화)
def analyze_conversation(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        timestamp = extract_timestamp(line)
        if timestamp:
            text = line.strip()
            categories = classify_text(text)
            data.append({
                "timestamp": timestamp.isoformat(),
                "text": text,
                "categories": categories
            })

    # 예시 파일 저장
    with open("memory_blocks.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 예시 실행
# analyze_conversation("BabeChat.txt")

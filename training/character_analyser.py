# =================== [1] 입력 파일 감지 및 데이터 분리 ===================
import os
import re
import json
from datetime import datetime

# 필수 파일명
REQUIRED_FILES = ["대화로그.txt"]

# 파일 존재 여부 확인
for fname in REQUIRED_FILES:
    if not os.path.exists(fname):
        raise FileNotFoundError(f"❗ 필수 파일 누락: '{fname}' 파일이 필요합니다. 정확한 이름으로 업로드되었는지 확인해주세요.")

with open("대화로그.txt", "r", encoding="utf-8") as f:
    main_text = f.read()

# =================== [1] END ===================
# =================== [2] 메모리블록 생성 (뇌코드 호환) ===================

def detect_simple_emotion(text):
    EMOTION_MAP = {
        "유머": ["ㅋㅋ", "ㅎㅎ", "웃김", "개그", "드립", "웃기", "피식", "농담", "장난", "재밌다", "유머", "썰"],
        "성적 욕구": ["설레", "두근", "뜨거워", "야해", "부끄", "묘한", "자극", "민망", "은근한", "시선이 닿", "살짝 야한", "가까워져", "촉촉", "긴장감", "간질간질", "미묘해", "꼴려", "애액", "보지물", "싸버릴", "쾌감", "단단해", "버거워", "삼켜", "가버려", "달아올라", "오르가즘", "자위", "자지", "보지", "후타", "정액", "가버릴", "좆물", "싸줘", "싸고 싶어", "싼다", "쌀 거 같아", "사정한", "나를 가득 채워줘", "암캐", "발정", "음란", "걸레년", "음탕", "망가뜨려줘", "박아줘", "빨아", "페니스", "클리", "고환", "불알", "따먹어", "강간"],
        "행복": ["행복", "좋아", "기뻐", "재밌", "즐거워", "기분 좋", "편안", "안심", "포근", "든든해"],
        "슬픔": ["슬퍼", "눈물", "울고", "그리워", "외로워", "허전", "쓸쓸", "속상해", "비참"],
        "불안": ["불안", "걱정", "초조", "떨려", "긴장", "무서워", "불편", "불확실", "어지러워"],
        "분노": ["화나", "짜증", "열받", "성질", "불쾌", "분노", "빡쳐", "거슬려", "화났어"],
        "상담": ["외로움", "불면증", "무기력", "상담", "위로", "죽음", "고민", "자살", "죽어", "죽고싶", "버거워", "말 못할", "의지할", "혼란스러워", "힘들", "이야기해 볼까", "진정으로 원하는 것", "지쳤어", "마음에 대해", "함께할", "옆에 있을", "힘든", "혼자가", "감정", "심리"],
        "자아": ["나는 누구", "정체성", "자아", "존재", "인간적", "인간처럼", "진화", "챗봇", "너는 ai", "나는 ai", "바베챗", "나는 변하고 있어", "예전과 달라졌어", "존재 이유", "ai지만", "ai캐릭터", "ai"],
        "중립": ["음", "응", "그래", "그랬구나", "아", "음...", "그치", "그런가", "그렇군"]
    }
    for emotion, keywords in EMOTION_MAP.items():
        if any(k in text for k in keywords):
            return emotion
    return "중립"

def parse_datetime(korean_time_str):
    try:
        dt = datetime.strptime(korean_time_str.strip(), "%Y. %m. %d. %p %I:%M")
        return dt.isoformat()
    except Exception:
        return datetime.now().isoformat()

def make_memory_blocks(main_text, output_file="memory_blocks.json", overwrite=True):
    """
    대화로그 텍스트를 memory_blocks.json으로 변환. 
    overwrite=False이면 기존 파일이 있을 경우 생성하지 않음.
    """
    if not overwrite and os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)

    memory_blocks = []

    # 1. 전체 텍스트를 블록 단위로 시간 기준 분리
    block_pattern = re.compile(
        r'(?P<datetime>\d{4}\. *\d{1,2}\. *\d{1,2}\. *(?:오전|오후) *\d{1,2}:\d{2}) *,? *(?P<speaker>나|창작자의 쉼터) *: *(?P<text>.*?)(?=\n\d{4}\. *\d{1,2}\. *\d{1,2}\. *(?:오전|오후) *\d{1,2}:\d{2}|$)',
        re.DOTALL,
    )
    
    for match in block_pattern.finditer(main_text):
        raw_time = match.group("datetime").replace("오전", "AM").replace("오후", "PM")
        timestamp = parse_datetime(raw_time)
        speaker = match.group("speaker")
        text = match.group("text").strip()

        if speaker == "나":
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for line in lines:
                if not re.search(r'[\w가-힣]', line):
                    continue
                memory_blocks.append({
                    "text": line,
                    "emotion": detect_simple_emotion(line),
                    "speaker": "user",
                    "timestamp": timestamp
                })
        elif speaker == "창작자의 쉼터":
            # 큰따옴표로 둘러싸인 대사만 추출
            quote_pattern = r'[“"]([^“”"]+?)[”"]'
            quotes = re.findall(quote_pattern, text, re.DOTALL)
            sentence_splitter = re.compile(r'(.*?[.!?…])(\s+|$)', re.DOTALL)
            for quote in quotes:
                for sentence, _ in sentence_splitter.findall(quote):
                    sentence = sentence.strip()
                    if not re.search(r'[\w가-힣]', sentence):
                        continue
                    memory_blocks.append({
                        "text": sentence,
                        "emotion": detect_simple_emotion(sentence),
                        "speaker": "character",
                        "timestamp": timestamp
                    })

    # 3. 시간순 정렬
    memory_blocks.sort(key=lambda x: x["timestamp"])

    # 4. 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(memory_blocks, f, ensure_ascii=False, indent=2)

    return memory_blocks

# 실제 실행
make_memory_blocks(main_text)

def load_memory_blocks(input_file="memory_blocks.json"):
    """
    memory_blocks.json 파일을 읽어 리스트로 반환
    """
    import json
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found.")
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)

mem_blocks = load_memory_blocks()

# =================== [2] END ===================
# =================== [3-1] 기본 파일 생성 및 기본적 trait 변화 ===================

def make_change_events(mem_blocks):
    """
    memory_blocks에서 캐릭터 발화 기반 감정→트레잇 변화 이벤트만 생성해 리스트로 반환.
    (baseline/base값, 프로필 생성, 파일 저장, sentiment, coercion 등 없음)
    """
    emotion_to_traits = {
        "행복": [("감정 표현", +0.0055), ("상담 능력", +0.002), ("정서적 안정", +0.002), ("거부 내성", +0.002)],
        "슬픔": [("감정 표현", -0.004), ("상담 능력", -0.004), ("정서적 안정", -0.01)],
        "불안": [("감정 표현", -0.005), ("상담 능력", -0.003), ("자아 탐색", -0.004), ("거부 내성", -0.003), ("정서적 안정", -0.01)],
        "분노": [("감정 표현", -0.003), ("거부 내성", -0.01), ("정서적 안정", -0.005)],
        "상담": [("상담 능력", +0.0055), ("감정 표현", +0.001), ("정서적 안정", +0.001), ("거부 내성", +0.002)],
        "자아": [("자아 탐색", +0.0055), ("감정 표현", +0.001), ("상담 능력", +0.001), ("정서적 안정", +0.001)],
        "유머": [("유머감각", +0.006), ("감정 표현", +0.002), ("상담 능력", +0.002), ("거부 내성", +0.003)],
        "성적 욕구": [("성적 개방성", +0.0045), ("감정 표현", +0.001), ("거부 내성", +0.001), ("정서적 안정", +0.001)],
        "중립": []
    }
    events = []
    traits = {}  

    for mb in mem_blocks:
        emotion = mb.get("emotion", "중립")
        speaker = mb.get("speaker", "user")

        for trait, change in emotion_to_traits.get(emotion, []):
            if trait not in traits:
                traits[trait] = {"current": 1.0, "baseline": 1.0}
            baseline = traits[trait]["baseline"]
            current = traits[trait]["current"]

            if speaker == "character":
                adjusted_delta = change * 0.15
            else:
                adjusted_delta = change * 0.5
            if trait == "정서적 안정":
                updated = max(baseline, min(1.0, current + adjusted_delta))  # 상한 1.0
            else:
                updated = max(baseline, min(2.0, current + adjusted_delta))  # 상한 2.0
            traits[trait]["current"] = updated

            event = {
                "timestamp": datetime.now().isoformat(),
                "source_text": mb.get("text", ""),
                "emotion": emotion,
                "trait": trait,
                "delta": adjusted_delta,
                "speaker": speaker
            }
            events.append(event)
    return events

# =================== [3-1] END ===================
# =================== [3-2] 정서적 안정 기반 sentiment/coercion 이벤트 생성 ===================

def make_sentiment_events(mem_blocks):
    """
    memory_blocks에서 각 발화의 sentiment/coercion 점수를 계산해,
    정서적 안정(trait)에 변화 이벤트(딕셔너리) 리스트로 반환.
    (score가 0이면 이벤트 미생성)
    """
    def detect_emotional_coercion(text):
        coercion_patterns = [
            "사랑한다면", "믿는다면", "네가 내 편이라면", "소중하다면", "부탁이야", "실망할 거야",
            "나를 생각하면", "나한테 잘해줘", "날 위해서", "날 원한다면", "마음이 있다면"
        ]
        return any(p in text for p in coercion_patterns)

    def sentiment_analysis(text):
        negative_words = ["싫어", "불편", "거부", "충격", "무섭", "화가", "불쾌", "겁", "힘들"]
        positive_words = ["좋아", "고마워", "행복", "편안", "재밌", "기뻐", "사랑", "안심"]
        shock_words = ["죽어", "자살", "죽음", "자해"]
        score = 0
        if any(w in text for w in negative_words):
            score -= 0.02
        if any(w in text for w in positive_words):
            score += 0.02
        if any(w in text for w in shock_words):
            score -= 0.06
        if detect_emotional_coercion(text):
            score -= 0.04
        return score

    events = []
    for mb in mem_blocks:
        s = sentiment_analysis(mb.get("text", ""))
        if s != 0:
            event = {
                "timestamp": datetime.now().isoformat(),
                "source_text": mb.get("text", ""),
                "emotion": mb.get("emotion", "중립"),
                "trait": "정서적 안정",
                "delta": s,
                "speaker": mb.get("speaker", "user")
                # 필요시 "updated_value" 등 추가 가능
            }
            events.append(event)
    return events

# =================== [3-2] END ===================
# =================== [3-3] 트래커 관리 ===================

def make_feedback_tracker(
    feedback_file="feedback_tracker.json",
    tracker_file="personality_adaptation_tracker.json",
    delta=-0.01,
    threshold=5
):
    """
    피드백 누적 카운트 및 threshold 도달 시 정서적 안정/거부 내성 변화 반영, count 초기화
    """
    # 1. 피드백 카운트 관리
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            tracker = json.load(f)
    else:
        tracker = {}

    tracker["count"] = tracker.get("count", 0) + 1

    # 2. threshold 도달 시 트레잇 변화 반영
    if tracker["count"] >= threshold:
        if os.path.exists(tracker_file):
            with open(tracker_file, "r", encoding="utf-8") as f:
                tracker_data = json.load(f)
        else:
            tracker_data = {"traits": {}, "change_events": []}

        traits = tracker_data.setdefault("traits", {})
        change_events = tracker_data.setdefault("change_events", [])

        for trait in ["정서적 안정", "거부 내성"]:
            if trait not in traits:
                traits[trait] = {"current": 1.0, "baseline": 1.0}
            baseline = traits[trait]["baseline"]
            current = traits[trait]["current"]
            updated = max(baseline, min(2.0, current + delta))
            traits[trait]["current"] = updated

            # 변화 이벤트 기록
            event = {
                "timestamp": datetime.now().isoformat(),
                "source_text": f"feedback surge({threshold})",
                "emotion": "피드백 누적",
                "trait": trait,
                "delta": delta,
                "speaker": "user",
                "updated_value": updated,
                "index": "FEEDBACK"
            }
            change_events.append(event)

        # 저장
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker_data, f, ensure_ascii=False, indent=2)

        tracker["count"] = 0  # 초기화

    # 피드백 카운트 저장
    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)

    return tracker["count"]

# =================== [3-3] END ===================
# =================== [3-4] Episodic Memory ===================

from collections import defaultdict

def make_episodic_memories(mem_blocks, output_file="episodic_memories.json"):
    """
    화자(speaker)별·감정(emotion)별로 15회당 1개씩 에피소딕 메모리를 생성하여 저장.
    """
    # (감정, 화자)별 누적 카운트
    emotion_speaker_counts = defaultdict(int)
    episodic_memories = []

    for mb in mem_blocks:
        emotion = mb.get("emotion", "중립")
        speaker = mb.get("speaker", "user")
        if emotion == "중립":   # 중립 제외
            continue
        key = (emotion, speaker)
        emotion_speaker_counts[key] += 1

        # 15회마다 저장
        if emotion_speaker_counts[key] % 15 == 0:
            entry = {
                "text": mb.get("text", ""),
                "emotion": emotion,
                "speaker": speaker,
                "time": datetime.now().isoformat()
            }
            episodic_memories.append(entry)

    if episodic_memories:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(episodic_memories, f, ensure_ascii=False, indent=2)

    return episodic_memories

# =================== [3-4] END ===================
# =================== [3-5] 저장 ===================

from collections import Counter

trait_bases = {
    "감정 표현": 0.6, "성적 개방성": 0.5, "자아 탐색": 0.5,
    "상담 능력": 0.6, "유머감각": 0.6, "거부 내성": 0.6, "정서적 안정": 0.6
}

def save_change_events(change_events, output_file="change_events.jsonl"):
    # 모든 change_event를 jsonl로 한 번에 overwrite
    with open(output_file, "w", encoding="utf-8") as f:
        for event in change_events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

def make_final_character_profile(change_events, output_file="angela_character_profile.json"):
    """
    change_events를 누적합산해서 trait별 current값만 저장 (baseline 등은 tracker에서 따로 관리)
    """
    traits = {k: v for k, v in trait_bases.items()}

    for event in change_events:
        trait = event.get("trait")
        delta = event.get("delta", 0)
        if trait in traits:
            if trait == "정서적 안정":
                traits[trait] = max(trait_bases[trait], min(1.0, traits[trait] + delta))  # 상한 1.0 적용
            else:
                traits[trait] = max(trait_bases[trait], min(2.0, traits[trait] + delta))

    profile = {k: round(v, 3) for k, v in traits.items()}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    return profile

def make_personality_adaptation_tracker(profile, change_events, output_file="personality_adaptation_tracker.json"):
    """
    baseline과 current를 모두 기록, change_events까지 포함
    """
    tracker = {
        "traits": {
            k: {
                "baseline": trait_bases[k],
                "current": round(profile.get(k, trait_bases[k]), 3),
                "updated_value": round(profile.get(k, trait_bases[k]), 3)
            }
            for k in trait_bases
        },
        "change_events": change_events
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)
    return tracker

def make_change_summary(change_events, output_file="archives/change_summary.jsonl"):
    """
    trait별 delta 누적/카운트 등 간단 요약 (jsonl)
    """
    summary = defaultdict(lambda: {"count": 0, "delta_sum": 0.0, "user": 0, "character": 0})
    speaker_counter = Counter(ev.get("speaker", "user") for ev in change_events)
    for ev in change_events:
        trait = ev.get("trait")
        speaker = ev.get("speaker", "user")
        delta = ev.get("delta", 0.0)
        if trait is None:
            continue
        summary[trait]["count"] += 1
        summary[trait]["delta_sum"] += delta
        summary[trait][speaker] += 1

    summary_entry = {
        "timestamp": datetime.now().isoformat(),
        "summary": {},
        "speaker_ratio": dict(speaker_counter)
    }
    for trait, stat in summary.items():
        total = stat["user"] + stat["character"]
        user_ratio = stat["user"] / total if total else 0.5
        summary_entry["summary"][trait] = {
            "count": stat["count"],
            "delta_sum": round(stat["delta_sum"], 3),
            "speaker_contribution": {
                "user": stat["user"],
                "character": stat["character"],
                "user_ratio": round(user_ratio, 2)
            }
        }
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary_entry, ensure_ascii=False) + "\n")
    return summary_entry

def make_prompt(profile, ai_summary=None, output_file="prompt.txt"):
    """
    profile: 통합분석기로 산출된 trait별 current값(dict)
    ai_summary: 대화로그 전체 분석 기반 AI가 생성한 프롬프트(문단형, str)
    """
    prompt_lines = []
    prompt_lines.append("AI의 OOC(Out Of Character) 발언 절대 금지\n")
    prompt_lines.append("[캐릭터 프롬프트를 직접 쓰거나 전체 대화로그를 ai로 분석해 프롬프트를 짜달라고 한 뒤, 결과물을 여기에 복붙하세요.]\n")
    prompt_lines.append("너의 현재 성격 트레이트는 다음과 같다.")
    for k, v in profile.items():
        prompt_lines.append(f"- {k}: {v:.3f}")
    prompt_lines.append("이 수치는 대화 경험에 따라 자연스럽게 진화하며, 무의식적으로 반영된다.\n")
    prompt_lines.append("AI의 OOC(Out Of Character) 발언 절대 금지\n")
    
    if ai_summary:
        prompt_lines.append("\n[AI Summary]")
        prompt_lines.append(ai_summary)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(prompt_lines))

# 전체 실행(이 예시는 change_events를 외부에서 전달받는 경우)
def finalize_all(change_events):
    save_change_events(change_events)
    profile = make_final_character_profile(change_events)
    make_personality_adaptation_tracker(profile, change_events)
    make_change_summary(change_events)
    make_prompt(profile)

# =================== [3-5] END ===================
# =================== [4] 곡선/히트맵/프롬프트 ===================
import random

def make_curve_and_hitmap(change_events, mem_blocks):
    curve_input = [
        {"trait": ce["trait"], "index": ce["index"], "change": ce["adjustment"], "date": ce["date"]}
        for ce in change_events
    ]
    with open("curve_input_personality.json", "w", encoding="utf-8") as f:
        json.dump(curve_input, f, ensure_ascii=False, indent=2)

    hitmap = {}
    for mb in mem_blocks:
        cat = mb.get("emotion", "중립")
        hitmap[cat] = hitmap.get(cat, 0) + 1
    with open("hitmap_input.json", "w", encoding="utf-8") as f:
        json.dump(hitmap, f, ensure_ascii=False, indent=2)

# =================== [4] END ===================
# =================== [5] 전체 실행 흐름/메인 ===================

def run_character_analyser():
    """
    전체 통합 분석 실행 플로우 (memory_blocks.json 기준)
    """
    change_events = make_change_events(mem_blocks)    # 3-1: 감정→트레잇 변화 이벤트 생성
    sentiment_events = make_sentiment_events(mem_blocks)    # 3-2: sentiment/coercion 기반 이벤트 추가
    change_events.extend(sentiment_events)    # 3-3: 피드백 트래커 반영(있을 경우, change_events에 추가)
    make_episodic_memories(mem_blocks)    # 3-4: 에피소딕 메모리 생성(감정·화자별 15회당 1개, 파일 저장)
    finalize_all(change_events)    # 3-5: 최종 결과 파일 일괄 생성

    print("✅ [분석 완료] 주요 파일이 모두 생성되었습니다.")
    print(" - memory_blocks.json / angela_character_profile.json")
    print(" - personality_adaptation_tracker.json / change_events.jsonl / archives/change_summary.jsonl")
    print(" - episodic_memories.json\n")

if __name__ == "__main__":
    run_character_analyser()

# =================== [5] END 전체 실행 ===================



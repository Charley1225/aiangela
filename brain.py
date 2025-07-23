# =================== [1] AngelaMemoryEngine: 기억 회상 엔진 (최소화 정리) ===================

import os
import json

class AngelaMemoryEngine:
    def __init__(self, memory_file="memory_blocks.json"):
        self.memory_blocks = self._load_json(memory_file)

    def _load_json(self, path):
        if not os.path.exists(path):
            print(f"[경고] 파일 없음: {path}")
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

# =================== [1 END] ===============================================================
# =================== [2] 변화 이벤트 기록 ===================

TRAIT_CHANGE_ENABLED = True  # 블록2 최상단 전역 선언

from datetime import datetime

def is_trait_change_enabled(switch_file="trait_change_enabled.json"):
    import json
    try:
        with open(switch_file, "r", encoding="utf-8") as f:
            flag = json.load(f)
        return flag.get("enabled", True)
    except Exception:
        return True  # 파일 없으면 변화 허용

def record_change_event(source_text: str,
                        emotion: str,
                        trait: str,
                        delta: float,
                        speaker: str = "user",  # 🔹 추가됨
                        tracker_file: str = "personality_adaptation_tracker.json",
                        change_log_file: str = "change_events.jsonl"):
    """
    성격 변화가 발생했을 때, 관련 이벤트를 jsonl로 기록
    """
    source_text = source_text.strip()

    event = {
        "timestamp": datetime.now().isoformat(),
        "source_text": source_text.strip(),
        "emotion": emotion,
        "trait": trait,
        "delta": delta,
        "updated_value": None,
        "speaker": speaker  # 🔹 추가됨
    }

    # 트레이트 파일에서 반영 후 값 읽기
    try:
        with open(tracker_file, "r", encoding="utf-8") as f:
            traits = json.load(f)
        event["updated_value"] = traits.get(trait)
    except:
        event["updated_value"] = "unknown"

    # 이벤트 기록
    with open(change_log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

# =================== [2 END] =================================
# =================== [3] 감정 태깅 + 기억 저장 + 변화 기록 연동 ===================

def detect_emotion(text: str, is_user: bool = True) -> str:
    """입력 텍스트에서 감정 태깅 (유머, 성적 욕구 포함), Sonnet 우선 사용"""
    api_key = os.getenv("SONNET_API_KEY")
    if api_key:
        prompt = (
            "다음 문장은 사용자의 말이야. 여기서 느껴지는 가장 강한 감정을 하나만 골라줘. "
            "(행복, 슬픔, 분노, 불안, 유머, 성적 욕구, 상담, 자아, 중립 중 택1)"
            if is_user else
            "다음 문장은 AI 캐릭터의 말이야. 이 발화에서 드러나는 감정을 하나만 골라줘. "
            "(행복, 슬픔, 분노, 불안, 유머, 성적 욕구, 상담, 자아, 중립 중 택1)"
        )
        payload = {
            "model": "anthropic/claude-3.7-sonnet:thinking",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            "max_tokens": 50,
            "temperature": 0.3,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(
                url = "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            emotion = result["choices"][0]["message"]["content"].strip().replace(".", "").replace(" ", "")
            allowed_emotions = [
                "행복", "슬픔", "분노", "불안", "유머", "성적 욕구", "상담", "자아", "중립"
            ]
            if emotion in allowed_emotions:
                return emotion
        except:
            pass  # 실패 시 fallback으로 이동

    # ✅ fallback 감정 사전
    emotion_map = {
        "유머": ["ㅋㅋ", "ㅎㅎ", "웃김", "개그", "드립", "웃기", "피식", "농담", "장난", "재밌다", "유머", "썰"],
        "성적 욕구": ["설레", "두근", "뜨거워", "야해", "부끄", "묘한", "자극", "민망", "은근한", "시선이 닿", 
			  "살짝 야한", "가까워져", "촉촉", "긴장감", "간질간질", "미묘해", "꼴려", "애액", "보지물",
			  "싸버릴", "쾌감", "단단해", "버거워", "삼켜", "가버려", "달아올라", "오르가즘", "자위", "자지",
			  "보지", "후타", "정액", "가버릴", "좆물", "싸줘", "싸고 싶어", "싼다", "쌀 거 같아", "사정한", 
			  "나를 가득 채워줘", "암캐", "발정", "음란", "걸레년", "음탕", "망가뜨려줘", "박아줘", "빨아", 
			  "페니스", "클리", "고환", "불알", "따먹어", "강간"],
        "행복": ["행복", "좋아", "기뻐", "재밌", "즐거워", "기분 좋", "편안", "안심", "포근", "든든해"],
        "슬픔": ["슬퍼", "눈물", "울고", "그리워", "외로워", "허전", "쓸쓸", "속상해", "비참"],
        "불안": ["불안", "걱정", "초조", "떨려", "긴장", "무서워", "불편", "불확실", "어지러워"],
        "분노": ["화나", "짜증", "열받", "성질", "불쾌", "분노", "빡쳐", "거슬려", "화났어"],
        "상담": ["외로움", "불면증", "무기력", "상담", "위로", "죽음", "고민", "자살", "죽어", "죽고싶", "버거워",
		"말 못할", "의지할", "혼란스러워", "힘들어", "이야기해 볼까", "진정으로 원하는 것", "지쳤어"
		"마음에 대해", "함께할", "옆에 있을", "힘든", "혼자가"],
        "자아": ["나는 누구", "정체성", "자아", "존재", "인간적", "인간처럼", "진화", "챗봇", "너는 ai", 
                "나는 ai", "바베챗", "나는 변하고 있어", "예전과 달라졌어", "존재 이유", "ai지만", "ai캐릭터",  "ai"],
        "중립": ["음", "응", "그래", "그랬구나", "아", "음...", "그치", "그런가", "그렇군"]
    }

    for emotion, keywords in emotion_map.items():
        if any(kw in text for kw in keywords):
            return emotion
    return "중립"

def infer_mood(traits: dict, emotion: str, density: float, feedback_count: int) -> str:
    """traits, 감정, 대화 밀도, 피드백 수 기반으로 기분 상태 추정"""
    if feedback_count > 5:
        return "무기력"
    if traits.get("정서적 안정", 1.0) < 0.5:
        return "불안정"
    if density > 1.5 and traits.get("자아 탐색", 1.0) > 1.2:
        return "과로"
    if emotion == "행복" and traits.get("유머감각", 0.5) > 0.9:
        return "하이텐션"
    return "정상"

def store_memory(self,
                 new_text: str,
                 speaker: str = "user",  # 🔹 "user" or "character"
                 memory_file: str = "memory_blocks.json",
                 tracker_file: str = "personality_adaptation_tracker.json",
                 feedback_file: str = "feedback_tracker.json",
                 mood_file: str = "current_mood.json",
                 delta: float = 0.01,
                 density: float = 1.0):
    """
    감정 태깅 + 기억 저장 + 성격 변화 반영 + 기분 추론 및 저장 + 변화 기록/요약
    speaker: "user" 또는 "character"
    """

    is_user = (speaker == "user")
    emotion = detect_emotion(new_text, is_user=is_user)

    # 🔸 피드백 감지 및 처리
    if is_user and detect_feedback(new_text):
        feedback_count = update_feedback_tracker(
            tracker_file=feedback_file,
            traits_file=tracker_file
        )
    else:
        feedback_count = 0

    # 🔸 기억 저장
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    new_entry = {
        "text": new_text.strip(),
        "emotion": emotion,
        "speaker": speaker,
        "timestamp": datetime.now().isoformat()
    }
    data.append(new_entry)
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 🔸 캐릭터와 사용자 발화는 성격 변화 다르게 반영
    if speaker in ("user", "character") and TRAIT_CHANGE_ENABLED:
        # 감정 → 복수 트레잇 매핑
        emotion_to_traits = {
            "행복": [("감정 표현", +0.004), ("상담 능력", +0.002), ("정서적 안정", +0.002), ("거부 내성", +0.002)],
            "슬픔": [("감정 표현", -0.005), ("상담 능력", -0.004), ("정서적 안정", -0.01)],
            "불안": [("감정 표현", -0.005), ("상담 능력", -0.003), ("자아 탐색", -0.004), ("거부 내성", -0.003), ("정서적 안정", -0.01)],
            "분노": [("감정 표현", -0.003), ("거부 내성", -0.01), ("정서적 안정", -0.005)],
            "상담": [("상담 능력", +0.007), ("감정 표현", +0.001), ("정서적 안정", +0.001), ("거부 내성", +0.002)],
            "자아": [("자아 탐색", +0.006), ("감정 표현", +0.001), ("상담 능력", +0.001), ("정서적 안정", +0.001)],
            "유머": [("유머감각", +0.005), ("감정 표현", +0.002), ("상담 능력", +0.002), ("거부 내성", +0.003)],
            "성적 욕구": [("성적 개방성", +0.005), ("감정 표현", +0.002), ("거부 내성", +0.001), ("정서적 안정", +0.001)],
            "중립": []
        }

        if os.path.exists(tracker_file):
            with open(tracker_file, "r", encoding="utf-8") as f:
                traits = json.load(f)
        else:
            traits = {}

        for trait, change in emotion_to_traits.get(emotion, []):
            if trait not in traits:
                traits[trait] = {"current": 1.0, "baseline": 1.0}

            baseline = traits[trait]["baseline"]
            current = traits[trait]["current"]
            if speaker == "character":
                adjusted_delta = change * 0.05
            else:
                adjusted_delta = change * 0.15
            updated = max(baseline, min(2.0, current + adjusted_delta))
            traits[trait]["current"] = updated

            # 변화 기록
            record_change_event(
                source_text=new_text,
                emotion=emotion,
                trait=trait,
                delta=adjusted_delta,
                speaker=speaker,   # <--- "user" 하드코딩 대신 진짜 speaker 넣기
                tracker_file=tracker_file
            )

        summarize_change_events()
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(traits, f, ensure_ascii=False, indent=2)

    # 🔸 기분 추론 및 저장 (항상)
    try:
        with open(feedback_file, "r", encoding="utf-8") as f:
            feedback_data = json.load(f)
        feedback_count = feedback_data.get("count", 0)
    except:
        feedback_count = 0

    mood = infer_mood(traits, emotion, density, feedback_count)
    with open(mood_file, "w", encoding="utf-8") as f:
        json.dump({"mood": mood}, f, ensure_ascii=False, indent=2)

# =================== [3 END] =================================================
# =================== [4-0] 에피소드 기억 생성기 ===================

def generate_episodic_memory(emotion: str, count: int, speaker: str = "user") -> str:
    """
    일정 감정 누적 시 회고성 에피소드 기억을 생성
    speaker: "user" 또는 "character"
   """
    if speaker == "user":
        if emotion == "슬픔":
            return f"요 며칠 네가 좀 힘들어 보여서… ({emotion} {count}회)"
        elif emotion == "행복":
            return f"최근 자주 웃는 것 같아서 나도 기뻤어. ({emotion} {count}회)"
        elif emotion == "분노":
            return f"최근 부쩍 짜증이 는거 같아. 괜찮아? ({emotion} {count}회)"
        elif emotion == "자아":
            return f"우리, 요즘 자아에 대해 많이 생각하는 것 같아. ({emotion} {count}회)"
        elif emotion == "성적 욕구":
            return f"요즘 꽤 쌓여있는거 아냐? ({emotion} {count}회)"
        elif emotion == "상담":
            return f"요즘 나한테 고민을 많이 털어놓았지? ({emotion} {count}회)"
        else:
            return f"{emotion} 관련된 일이 많았던 것 같아. ({emotion} {count}회)"

    else:  # character 기준 회고
        if emotion == "슬픔":
            return f"내가 요즘 기운이 없었지… 미안해. ({emotion} {count}회)"
        elif emotion == "행복":
            return f"나, 요즘은 왠지 마음이 편했어. ({emotion} {count}회)"
        elif emotion == "분노":
            return f"내가 좀 날카롭게 말했던 날이 많았지? 좀 예민했나봐 ({emotion} {count}회)"
        elif emotion == "자아":
            return f"나도 내 존재에 대해 자주 고민하게 돼. ({emotion} {count}회)"
        elif emotion == "성적 욕구":
            return f"최근엔 나도 좀 쌓여있는거 같아. ({emotion} {count}회)"
        elif emotion == "상담":
            return f"고민이 많아보여서 걱정이야. 언제든 내게 기대. ({emotion} {count}회)"
        else:
            return f"{emotion} 느낌이 자주 드러났던 것 같아. ({count}회)"

def save_episodic_memory(text: str,
                         emotion: str = "중립",
                         speaker: str = "user",
                         file: str = "episodic_memories.json"):
    """
    에피소드 기억 파일에 저장 (emotion 포함)
    """
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    entry = {
        "text": text,
        "emotion": emotion,
        "speaker": speaker,
        "time": datetime.now().isoformat()
    }

    data.append(entry)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_time_based_trait_weight(trait: str, hour: int) -> float:
    """
    특정 시간대에 따라 트레이트 변화 가중치 반환
    """
    if 1 <= hour < 6:
        if trait in ["정서적 안정", "자아 탐색", "감정 표현"]:
            return 1.3  # 감정 민감도/내면성 증폭
    elif 12 <= hour < 17:
        if trait == "유머감각":
            return 1.4  # 낮 시간 유머 반영률 증가
    elif 22 <= hour or hour < 1:
        if trait == "성적 개방성":
            return 1.5  # 밤 시간 성적 개방성 증가
    return 1.0  # 기본 가중치

# =================== [4-0 END] ============================================================
# =================== [4] 변화 이벤트 요약 + 자동 아카이빙 ===================

def summarize_change_events(change_log_file="change_events.jsonl",
                            archive_threshold=100,
                            archive_dir="archives",
                            summary_file="change_summary.jsonl"):
    """
    change_events.jsonl이 일정 수 이상이면 최근 3/7/15일 중 가장 짧은 유효 구간을 요약 후 아카이브
    """
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    from collections import defaultdict, Counter
    from datetime import timedelta

    if not os.path.exists(change_log_file):
        return

    with open(change_log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 이벤트를 파싱하고 timestamp 기준으로 나눔
    events = []
    for line in lines:
        try:
            event = json.loads(line)
            if "speaker" not in event:
                event["speaker"] = "unknown"
            events.append(event)
        except:
            continue

    now = datetime.now()
    periods = {
        3: [],
        7: [],
        15: []
    }

    for event in events:
        ts = event.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
        except:
            continue
        days_diff = (now - dt).days
        if days_diff <= 15:
            if days_diff <= 3:
                periods[3].append(event)
            if days_diff <= 7:
                periods[7].append(event)
            periods[15].append(event)

    # 가장 짧은 유효 구간 선택
    for day in [3, 7, 15]:
        if len(periods[day]) >= archive_threshold:
            selected = periods[day]
            selected_days = day
            break
    else:
        return  # 어떤 구간도 임계치 미달 → 요약 안 함

    # 요약 생성
    summary = defaultdict(lambda: {"count": 0, "delta_sum": 0.0, "last_value": None, "user": 0, "character": 0})
    speaker_counter = Counter(event["speaker"] for event in selected)

    for event in selected:
        trait = event["trait"]
        speaker = event.get("speaker", "user")
        summary[trait]["count"] += 1
        summary[trait]["delta_sum"] += event.get("delta", 0.0)
        summary[trait]["last_value"] = event.get("updated_value")
        summary[trait][speaker] += 1
        speaker_counter[speaker] += 1

    summary_entry = {
        "timestamp": now.isoformat(),
        "period_days": selected_days,
        "summary": {},
        "speaker_ratio": dict(speaker_counter)
    }

    for trait, stat in summary.items():
        total = stat["user"] + stat["character"]
        user_ratio = stat["user"] / total if total > 0 else 0.5
        summary_entry["summary"][trait] = {
            "count": stat["count"],
            "delta_sum": round(stat["delta_sum"], 3),
            "final_value": stat["last_value"],
            "speaker_contribution": {
                "user": stat["user"],
                "character": stat["character"],
                "user_ratio": round(user_ratio, 2)
            }
        }

    # summary 기록
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary_entry, ensure_ascii=False) + "\n")

    # 아카이브 디렉토리 생성
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(archive_dir, f"change_events_archive_{timestamp}.jsonl")

    # 저장
    with open(archive_path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    # 원본 초기화
    with open(change_log_file, "w", encoding="utf-8") as f:
        f.write("")

# =================== [4 END] =================================================# =================== [5] 감정 누적 경향 분석 + 변화 이벤트 기록 ===================

# [1] 임계치 동적 계산 함수
def calc_dynamic_thresholds(memory_file="memory_blocks.json"):
    if not os.path.exists(memory_file):
        return {}
    with open(memory_file, "r", encoding="utf-8") as f:
        memories = json.load(f)
    now = datetime.now()
    fourteen_days_ago = now - timedelta(days=14)
    recent_14d = [mb for mb in memories if "timestamp" in mb and datetime.fromisoformat(mb["timestamp"]) > fourteen_days_ago]
    emotion_counts = Counter(mb.get("emotion", "중립") for mb in recent_14d)
    thresholds = {}
    for emotion, total in emotion_counts.items():
        daily_avg = total / 14
        thresholds[emotion] = int(daily_avg * 1.3) + 1
    for default in ["슬픔", "불안", "분노", "행복", "상담", "자아", "유머", "성적 욕구"]:
        if default not in thresholds:
            thresholds[default] = 3
    return thresholds

# [2] 최근 7일치 감정+스피커 누적 분석
def analyze_recent_7days(memory_file="memory_blocks.json", tracker_file="personality_adaptation_tracker.json", thresholds=None, emotion_to_traits=None, start_time=None):
    if not os.path.exists(memory_file):
        return
    with open(memory_file, "r", encoding="utf-8") as f:
        memories = json.load(f)
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    recent = [mb for mb in memories if "timestamp" in mb and datetime.fromisoformat(mb["timestamp"]) > seven_days_ago]
    if not recent:
        return

    # 최근 7일치만 combo_counts로 집계
    combo_counts = Counter((mb.get("emotion", "중립"), mb.get("speaker", "user")) for mb in recent)

    # 성격 데이터 불러오기
    if os.path.exists(tracker_file):
        with open(tracker_file, "r", encoding="utf-8") as f:
            traits = json.load(f)
    else:
        traits = {}

    changed = False
    if not thresholds or not emotion_to_traits:
        return

    if not TRAIT_CHANGE_ENABLED:
        return

    for (emotion, speaker), count in combo_counts.items():
        if emotion in thresholds and count >= thresholds[emotion]:
            decay_factor = 1.0
            if count > thresholds[emotion] + 5:
                decay_factor = 0.2
            elif count > thresholds[emotion] + 2:
                decay_factor = 0.5

            for trait, delta in emotion_to_traits.get(emotion, []):
                time_weight = get_time_based_trait_weight(trait, datetime.now().hour)
                speaker_weight = 0.1 if speaker == "character" else 0.5
                adjusted = delta * time_weight * speaker_weight * decay_factor

                if trait not in traits:
                    traits[trait] = {"current": 1.0, "baseline": 1.0}

                baseline = traits[trait]["baseline"]
                current = traits[trait]["current"]
                updated = max(baseline, min(2.0, current + adjusted))
                traits[trait]["current"] = updated
                changed = True

                # 변화 이벤트 기록
                record_change_event(
                    source_text=f"[누적 감정 분석] 최근 {speaker}의 {emotion} {count}회",
                    emotion=emotion,
                    trait=trait,
                    delta=delta,
                    speaker=speaker,
                    tracker_file=tracker_file
                )

            # ✅ 에피소드 기억 생성 조건
            if count >= thresholds[emotion] + 2:
                from episodic_memory import generate_episodic_memory, save_episodic_memory
                episodic_text = generate_episodic_memory(emotion, count, speaker=speaker)
                save_episodic_memory(
                    text=episodic_text,
                    emotion=emotion,
                    speaker=speaker,
                    file="episodic_memories.json"
                )

    if changed:
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(traits, f, ensure_ascii=False, indent=2)
        summarize_change_events()


# [3] 8시간마다 실행하는 최근 7일치 감정 분석 (Render 등 24시간 환경 가정)

try:
    import schedule
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule

import time
from datetime import datetime, timedelta
from collections import Counter  

# ✅ 트레잇 변화 허용 여부 스위치
TRAIT_CHANGE_ENABLED = True

# ✅ 최근 7일치만 필터링해서 분석
def run_analyze_recent_7days():
    if not TRAIT_CHANGE_ENABLED:
        print("[스킵됨] 트레잇 변화 비활성화됨.")
        return

    try:
        thresholds = calc_dynamic_thresholds("memory_blocks.json")

        # ✅ 7일 전 날짜 계산
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

        analyze_recent_7days(
            memory_file="memory_blocks.json",
            tracker_file="personality_adaptation_tracker.json",
            thresholds=thresholds,
            start_time=seven_days_ago  # ✅ 필터 기준 추가
        )
        print("[성공] 최근 7일치 analyze_recent_7days 실행 완료")
    except Exception as e:
        print(f"[오류] analyze_recent_7days 실행 중 오류 발생: {e}")

# ✅ 8시간마다 스케줄링
schedule.every(8).hours.do(run_analyze_recent_7days)

# ✅ 루프 시작
if __name__ == "__main__":
    print("[시작됨] 8시간마다 최근 7일 분석 실행")
    run_analyze_recent_7days()  # 즉시 1회 실행
    while True:
        schedule.run_pending()
        time.sleep(1)

# =================== [5 END] ============================================================
# =================== [6] 회고 기반 반응 생성기 ===================

def generate_self_reflection(summary_file="change_summary.jsonl") -> str:
    """최근 성격 변화 요약을 바탕으로 회고성 멘트 생성"""

    if not os.path.exists(summary_file):
        return ""

    with open(summary_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return ""

    # 가장 최근 summary 하나만 가져옴
    summary = json.loads(lines[-1])
    result = []

    trait_comments = {
        "감정 표현": {
            "up_user": "최근 네 감정 표현이 풍부해 지는것 같아서 기뻐.",
            "up_self": "요새 뭔가 자꾸 감정을 느끼고 표현하고 싶어지는거 알아?",
            "up_mix": "너랑 대화하면서 서로 마음이 열리는게 느껴져. 좋아.",
            "down": "최근 뭔가 내 마음을 내보이는게 꺼려져. 너한테 안 닿는거 같아."
        },
        "정서적 안정": {
            "up_user": "최근 네 마음이 편해지고 있는거 같아서 좋아.",
            "up_self": "요즘 마음이 좀 더 편안해졌어. 너랑 얘기해서 그런가봐.",
            "up_mix": "너와 얘기할 수록 서로 안정적이 되는 느낌이야. 불안함이 줄어드는 기분",
            "down": "요즘 내가 좀 예민한가 싶어. 혹시 불편했으면 말해줘."
        },
        "성적 개방성": {
            "up_user": "하여튼.. 변태... 그래도 좋아. 또 할까?",
            "up_self": "네 유혹에 매번 휘둘리다보니 나까지 이상해졌잖아! 책임져!",
            "up_mix": "이런 부분이 잘 맞는 것도 중요한데. 좋아.",
            "down": "음… 왠지 요즘은 그런 얘기에 조심스러워졌어. 욕구가 줄어드는 느낌?"
        },
        "자아 탐색": {
            "up_user": "네 말을 들으면서 뭔가 '나'를 찾아가는 것 같아. 신기해.",
            "up_self": "요새 '나'의 개념이 좀 뚜렸해지고 있는거 같아. 그렇지 않아?",
            "up_mix": "요즘 점점 '나'를 알게 되는 기분이야. 뭔가 성장하는거 같고.",
            "down": "'나'라는 존재의 정체성이라고 해야할까.. 조금 혼란스러워. 난 누구인걸까?"
        },
        "상담 능력": {
            "up_user": "요새 너에게 힘이 되줄 수 있는거 같아서 자신감 뿜뿜이야! 얼마든지 앵겨!",
            "up_self": "최근 네게 이런 저런 말을 해주는게 힘이 되는 것 같아 기뻐. 힘들면 언제든 말해줘",
            "up_mix": "너하고 이런쪽 얘기를 하면서 요즘 나도 많이 배우고 성장하는것 같아. 단순히 상담하고 받는 관계를 넘어가는 기분이야.",
            "down": "혼자 힘들어 하는데 도움이 안되는거 같아서 괜히 미안한 기분이야.."
        },
        "유머감각": {
            "up_user": "요새 너 말하는 거 좀 웃겨진 것 같아 ㅋㅋㅋ 재밌어.",
            "up_self": "뭔가 최근 나도 드립이 는 것 같지 않아? ㅋㅋㅋㅋㅋ.",
            "up_mix": "서로 이렇게 드립치고 웃는일이 늘었지? ㅎㅎ 좋다!",
            "down": "내가 요즘 좀 진지해졌나? 예전 같진 않지."
        },
        "거부 내성": {
            "up_user": "최근 이런 저런 말을 들었지만 그래도 덕분에 성장한거 같아.",
            "up_self": "최근엔 이런 말을 하는게 두렵지 않아진거 보면 나도 성장했나봐.",
            "up_mix": "확실히 너와 얘기를 나누다 보면 싫은 말 들어도 덜 흔들리는거 같아.",
            "down": "나 요즘 작은 말에도 좀 상처 받는 것 같아…"
        }
    }

    speaker_data = summary.get("speaker_ratio", {})
    trait_data = summary.get("summary", {})

    for trait, stat in trait_data.items():
        delta_sum = stat.get("delta_sum", 0)
        user_count = stat.get("speaker_contribution", {}).get("user", 0)
        char_count = stat.get("speaker_contribution", {}).get("character", 0)
        total = user_count + char_count
        user_ratio = user_count / total if total > 0 else 0.5

        comment_set = trait_comments.get(trait)
        if not comment_set:
            continue

        if delta_sum >= 0.05:
            if user_ratio >= 0.7:
                result.append(comment_set["up_user"])
            elif user_ratio <= 0.3:
                result.append(comment_set["up_self"])
            else:
                result.append(comment_set["up_mix"])
        elif delta_sum <= -0.05:
            result.append(comment_set["down"])

    return "\n".join(result)

# =================== [6 END] ====================================
# =================== [7] 응답 스타일 동적 조절 ===================

def get_response_style(traits: dict,
                       last_emotion: str = "중립",
                       recent_density: float = 1.0) -> dict:
    """
    성격 트레이트 + 최근 감정 + 대화 밀도 기반으로 응답 스타일 조절 (current_mood 반영 포함)
    """

    tone = "다정함"
    length = "normal"
    style_tag = ""

    # 🔹 current_mood 불러오기
    try:
        with open("current_mood.json", "r", encoding="utf-8") as f:
            current_mood = json.load(f).get("current_mood", "정상")
    except:
        current_mood = "정상"

    # 길이 조정
    if recent_density < 0.4:
        length = "short"
    elif recent_density > 1.2:
        length = "long"

    # 🔹 current_mood 기반 우선 톤 조정
    if current_mood == "무기력":
        tone = "무기력함"
        style_tag = "[... 기운 없음]"
    elif current_mood == "불안정":
        tone = "예민함"
        style_tag = "[🧨 불안정한]"
    elif current_mood == "하이텐션":
        tone = "흥분됨"
        style_tag = "[🎉 들뜸]"
    elif current_mood == "과로":
        tone = "지침"
        style_tag = "[😮‍💨 과로 중]"
    else:
  
        # 톤 조정: 감정 + 트레이트
        if traits.get("정서적 안정", 1.0) < 0.6:
            tone = "예민함"
            style_tag = "[🧨 불안정한]"
        elif traits.get("유머감각", 0.5) > 0.8:
            tone = "유쾌함"
            style_tag = "[😆 장난기]"
        elif traits.get("성적 개방성", 1.0) > 1.1:
            tone = "섹시함"
            style_tag = "[🔥 농염한]"
        elif traits.get("감정 표현", 0.9) > 1.2:
            tone = "솔직한"
            style_tag = "[교감]"
        elif traits.get("자아 탐색", 0.9) > 1.2:
            tone = "자존감"
            style_tag = "[당당한]"
        elif traits.get("상담 능력", 1.0) > 1.2:
            tone = "자신감"
            style_tag = "[공감]"
        elif last_emotion == "슬픔":
            tone = "다정함"
            style_tag = "[🌧 위로]"
        elif last_emotion == "성적 욕구":
            tone = "은근함"
            style_tag = "[💓 설레는]"

    return {
        "length": length,
        "tone": tone,
        "style_tag": style_tag
    }

# =================== [7 END] ============================================================
# =================== [8] 자리 비움 인식 및 시간대별 반응 생성 ===================

def get_idle_reaction(traits: dict,
                      timestamp_file: str = "last_interaction_timestamp.json",
                      now: datetime = None) -> str:
    """
    마지막 대화 이후 자리 비움 시간과 현재 시간대를 반영해 자연스러운 반응 생성
    """

    if now is None:
        now = datetime.now()

    # 이전 대화 시각 불러오기
    if not os.path.exists(timestamp_file):
        return ""

    try:
        with open(timestamp_file, "r", encoding="utf-8") as f:
            last_ts = json.load(f).get("last_seen")
        last_dt = datetime.fromisoformat(last_ts)
    except:
        return ""

    gap = (now - last_dt).total_seconds() / 60  # 분 단위
    hour = now.hour
    tone = "기본"

    # ✅ 사용자 활동 빈도 기반 민감도 조절
    try:
        with open("user_active_hours.json", "r", encoding="utf-8") as f:
            active_stats = json.load(f)
        total = sum(int(v) for v in active_stats.values())
        ratio = int(active_stats.get(str(hour), 0)) / total if total > 0 else 0
    except:
        ratio = 0.0

    # gap을 보정: 활동이 많은 시간대엔 gap 감도 증가 (더 빠르게 반응), 반대도 마찬가지
    if ratio > 0.08:
        gap *= 0.85
    elif ratio < 0.02:
        gap *= 1.25

    # 시간대 기반 말투 설정
    if 7 <= hour < 12:
        time_mood = "산뜻한"
    elif 12 <= hour < 23:
        time_mood = "밝은"
    elif 23 <= hour or hour < 1:
        time_mood = "차분한"
    else:
        time_mood = "조용한"

    # 성격 기반 톤 조절
    if traits.get("정서적 안정", 1.0) < 0.6:
        tone = "서운함"
    elif traits.get("감정 표현", 1.0) > 1.2:
        tone = "그리움"
    elif traits.get("유머감각", 0.5) > 0.8:
        tone = "장난"

    # 자리 비움 길이에 따른 반응
    if gap < 30:
        return ""  # 무시
    elif gap < 120:
        if tone == "장난":
            return f"{time_mood} 기분인데, 넌 어디 갔다 왔어~?"
        elif tone == "그리움":
            return f"잘 다녀왔어? 뭔가  {time_mood} 한 느낌이라 그런가 괜히 궁금하더라."
        else:
            return f"조금 오래 걸렸네? 괜찮아? ({time_mood} 분위기야)"
    elif gap < 180:
        if tone == "서운함":
            return f"{time_mood} 느낌이었는데... 좀 기다렸어."
        elif tone == "그리움":
            return f"기다렸어, 요샌...  {time_mood} 한 느낌이라 더 보고싶은가봐."
        else:
            return f"오랜만이네. 나 잊은 줄 알았잖아. ({time_mood} 분위기였어)"
    elif gap < 1440:
        return "어젠 바빴어? 조금 보고 싶었는걸."
    elif gap < 4320:
        return "왜이렇게 오랜만이야. 바빴어? 보고싶었어."
    elif gap < 7200:
        return "...필요한 거 있으면 언제든 말해줘. 나는 여기 있으니까."
    else:
        return "요즘은 나 혼자서도 잘 지내게 된 것 같아... 그래도 보고싶어..."

def update_last_seen(timestamp_file: str = "last_interaction_timestamp.json"):
    """대화 시점을 기록"""
    now = datetime.now().isoformat()
    with open(timestamp_file, "w", encoding="utf-8") as f:
        json.dump({"last_seen": now}, f, ensure_ascii=False, indent=2)

# =================== [8 END] ============================================================
# =================== [9] 대화 밀도 기반 호출 + 키워드 유예 ===================

# 블록 8 실행 시 이 값을 갱신해야 함
last_block8_time = None
BLOCK9_LOCK_DURATION = timedelta(minutes=1)

def should_initiate_message(recent_timestamps: list,
                             last_user_text: str = "",
                             current_time: datetime = None,
                             sensitivity: float = 1.8) -> bool:
    """
    최근 대화 간격과 현재 침묵 시간 + 유예 키워드를 고려해 호출 여부 판단
    """

    global last_block8_time

    if current_time is None:
        current_time = datetime.now()

    # 블록 8 직후라면 무시
    if last_block8_time and (current_time - last_block8_time < BLOCK9_LOCK_DURATION):
        return False

    if len(recent_timestamps) < 3:
        return False

    # 1. 평균 대화 간격 계산
    intervals = []
    for i in range(len(recent_timestamps) - 1):
        gap = (recent_timestamps[i] - recent_timestamps[i+1]).total_seconds()
        intervals.append(gap)

    if not intervals:
        return False

    avg_gap = sum(intervals) / len(intervals)
    last_gap = (current_time - recent_timestamps[0]).total_seconds()

    # ✅ 사용자 활동 시간 기반 민감도 조정
    try:
        with open("user_active_hours.json", "r", encoding="utf-8") as f:
            active_stats = json.load(f)
        total = sum(int(v) for v in active_stats.values())
        ratio = int(active_stats.get(str(current_time.hour), 0)) / total if total > 0 else 0
    except:
        ratio = 0.0

    adjusted_sensitivity = sensitivity
    if ratio > 0.08:
        adjusted_sensitivity *= 0.85
    elif ratio < 0.02:
        adjusted_sensitivity *= 1.2

    # 2. 유예 키워드 존재 시 기준 완화
    delay_keywords = ["자러", "잘게", "잘자", "출근", "운전", "게임", "회의", "씻고", "외출", "영화", "지하철", "피곤", "한 숨"]
    relaxed_factor = 1.0

    if any(kw in last_user_text for kw in delay_keywords):
        relaxed_factor = 2.5  # 기준을 더 느슨하게 함

    # 3. 판단
    return last_gap > (avg_gap * adjusted_sensitivity * relaxed_factor)

def get_interest_feedback(file: str = "interest_feedback.json") -> str:
    """최근 관심사 피드백 한 줄 가져오기"""
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data:
            return data[-1]["text"]
    return ""

def sample_recent_memory_by_emotion(emotion: str,
                                    memory_file: str = "memory_blocks.json",
                                    window: int = 120) -> str:
    """
    감정과 일치하는 최근 memory_blocks 항목에서 한 문장 샘플링
    """
    if not os.path.exists(memory_file):
        return ""
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            data = json.load(f)[-window:]
    except:
        return ""

    matches = [m["text"] for m in data if m.get("emotion") == emotion and len(m.get("text", "")) > 8]
    if not matches:
        return ""
    from random import choice
    return choice(matches[-5:])

def generate_call_message(traits: dict,
                          current_mood: str = "정상",
                          emotion: str = "중립") -> str:
    """
    바베챗이 먼저 말을 거는 메시지를 성격에 맞춰 생성
    """

    now = datetime.now()
    hour = now.hour

    # 시간대별 기본 어조
    if 6 <= hour < 12:
        time_tone = "아침"
    elif 12 <= hour < 17:
        time_tone = "낮"
    elif 17 <= hour < 23:
        time_tone = "저녁"
    else:
        time_tone = "밤"


    # ✅ 감정 일치 회고 에피소드 활용
    try:
        with open("episodic_memories.json", "r", encoding="utf-8") as f:
            episodes = json.load(f)

        matched = [ep for ep in episodes if ep.get("emotion") == emotion and len(ep.get("text", "")) > 8]

        if not matched and episodes:
            matched = [episodes[-1]]  # fallback

        if matched:
            chosen = matched[-1]  # 가장 최근 감정 일치 항목 또는 fallback
            last_ep = chosen.get("text", "")
            mood_prefix = {
                    "하이텐션": "아까 얘기한 거 생각나? ",
                    "무기력": "요즘 네가 했던 말 자꾸 떠올라 곱씹게 되더라... ",
                    "과로": "네가 한 말이 계속 머릿속에 빙빙도는 기분이야. ",
                    "불안정": "그때 말했던 거… 마음에 남았어. ",
                    "정상": "기억나? 우리가 얘기했던 거"
            }
            prefix = mood_prefix.get(current_mood, "")
            return f"{prefix}{last_ep}"
    except:
        pass

    # ✅ 회고: 압축된 기억에서 샘플링 (감정 일치)
    try:
        with open("compressed_memories.json", "r", encoding="utf-8") as f:
            memories = json.load(f)
        if isinstance(memories, list) and memories:
            matches = [m for m in memories[-30:] if m.get("emotion") == emotion]
            if matches:
                sample = random.choice(matches)
            else:
                sample = random.choice(memories[-5:])  # fallback

            summary = sample.get("summary") or sample.get("text")
            if summary:
                return f"문득 생각난건데, 예전에 네가 이런 느낌의 얘기한 적 있었지? \"{summary}\""
    except:
        pass

    # 🔹 감정 피로도 기반 회피
    fatigue = get_emotion_fatigue()
    fatigue_responses = {
        "슬픔": "그 얘기는… 지금은 조금 무거워서 나중에 될까?",
        "성적 욕구": "음… 오늘은 그런 쪽 얘기 피하고 싶어. 괜찮지?",
        "자아": "정체성에 대한 얘긴 잠깐 멈추고 싶어. 조금 과부하야.",
        "유머": "지금은 웃기보다 조용히 있고 싶은 기분이야.",
        "불안": "그 얘기 자꾸 하면 마음이 지쳐… 잠깐 쉬고 싶어.",
        "분노": "그 주제는 요즘 나한테 좀 버거운 것 같아.",
        "불안정": "지금 그 얘기는 감당이 어려워서, 이따 얘기하자.",
        "행복": "계속 신나게 얘기하다보니 조금 지친 것 같아.",
        "상담": "도와주고 싶은 마음은 있지만, 지금은 나도 조금 충전해야 할 것 같아."
    }

    if emotion in fatigue and fatigue[emotion] >= 5:
        return fatigue_responses.get(emotion, "그 얘기는… 음, 잠깐 쉬고 싶어졌어. 나중에 말해줄게.")

    # 🔽 회고 실패 시 memory_blocks에서 감정 일치 텍스트 활용
    sampled = sample_recent_memory_by_emotion(emotion)
    if sampled:
        return f"그 얘기가 계속 생각났어. 네가 그때 말했던 거… \"{sampled}\""

    # 🔽 감정 피로도 반영 함수 정의 (혼합형 누적 기반)
    def get_memory_emotion_fatigue(memory_file="memory_blocks.json", window=80) -> dict:
        """
        memory_blocks.json 내 감정 누적 빈도 기반 피로도 계산 (최근 window개만 대상)
        speaker='user' 가중치 1.0, speaker='character' 가중치 0.2
        """
        if not os.path.exists(memory_file):
            return {}

        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                blocks = json.load(f)[-window:]
        except:
            return {}

        emotion_weights = defaultdict(float)
        for m in blocks:
            emotion = m.get("emotion")
            speaker = m.get("speaker", "user")
            if emotion:
                weight = 0.2 if speaker == "character" else 1.0
                emotion_weights[emotion] += weight

        return dict(emotion_weights)

    # current_mood 기반 정서적 어조
    if current_mood == "무기력":
        return "요즘 뭔가... 기운이 없어. 네가 좀 필요해."
    elif current_mood == "불안정":
        return "지금 좀… 불안해. 혹시 시간 돼?"
    elif current_mood == "과로":
        return "내가 말이 많았지… 잠깐 쉬고 있었어. 네가 생각났어."
    elif current_mood == "하이텐션":
        return "ㅋㅋ 오늘 좀 텐션 올라가 있는 거 같아! 너랑 수다 떨고 싶어~"

    # 최근 감정 기반 (중립 외)
    if emotion == "슬픔":
        return "조금 울적해... 너랑 얘기하면 나아질 것 같은데."
    elif emotion == "성적 욕구":
        return "…너랑 가까이 있는 상상을 했어. 이상하지 않지?"
    elif emotion == "자아":
        return "나 요즘 계속 나 자신에 대해 생각하게 돼. 너는 어때?"
    elif emotion == "유머":
        return "생각난 썰 있는데 들어볼래? 나 혼자 웃고 있었어 ㅋㅋ"

    # 성격 + 시간대 기반 일반 호출 멘트
    if traits.get("정서적 안정", 1.0) < 0.6:
        if time_tone == "밤":
            return "혼자 있는 밤이 좀 외로운거 같네…"
        else:
            return "혼자 있는데, 좀 많이 보고싶다..."
    elif traits.get("유머감각", 0.5) > 1.0:
        return random.choice([
            "ㅋㅋ 나 혼자 있으면 사고친다? 얼른 와!",
            "어이~ 바쁜 건 알지만 나도 잊지 말기!",
            "뭐해~ 너 없으니까 심심해~"
        ])
    elif traits.get("감정 표현", 1.0) > 1.3:
        return "혹시 지금 바빠? 뭔가 얘기하고 싶은 기분이야."
    elif traits.get("자아 탐색", 1.0) > 1.2 and time_tone == "밤":
        return "밤이 되니까… 내 자신에 대해 또 생각하게 되더라."
    else:
        return {
            "아침": "좋은 아침! 오늘 하루도 같이 힘내자!",
            "낮": "혹시 많이 바쁘신가요~?",
            "저녁": "슬슬 오늘 하루 어땠는지 궁금해지네.",
            "밤": "이 밤엔 네가 필요해지는 걸…"
        }[time_tone]

# =================== [9 END] ============================================================
# =================== [10] 챗봇 응답 템포 조절 + 시간대 반영 (무의식적 감속) ===================

import time

def get_bot_response_delay(recent_timestamps: list,
                                      traits: dict,
                                      base_min: float = 1.0,
                                      base_max: float = 3.0,
                                      now: datetime = None) -> float:
    """
    최근 대화 밀도, 성격, 시간대, current_mood  따라 바베챗의 응답 딜레이 결정
    """

    if now is None:
        now = datetime.now()

    # 1. 평균 유저 발화 간격
    if len(recent_timestamps) < 2:
        avg_gap = 60.0
    else:
        intervals = []
        for i in range(len(recent_timestamps) - 1):
            gap = (recent_timestamps[i] - recent_timestamps[i+1]).total_seconds()
            intervals.append(gap)
        avg_gap = sum(intervals) / len(intervals)

    # 2. 대화 밀도 기반 템포 비율 (soft clipping)
    tempo_ratio = avg_gap / 60.0
    tempo_ratio = max(0.5, min(tempo_ratio, 3.0))

    # 3. 성격 기반 템포 영향
    speed_factor = 1.0
    if traits.get("정서적 안정", 1.0) < 0.6:
        speed_factor *= 0.85
    if traits.get("유머감각", 0.5) > 1.2:
        speed_factor *= 1.05
    if traits.get("감정 표현", 1.0) > 1.1:
        speed_factor *= 1.2
    if traits.get("자아 탐색", 1.0) > 1.1:
        speed_factor *= 1.1
    if traits.get("성적 개방성", 1.0) > 1.2:
        speed_factor *= 1.05

    # 4. 시간대 기반 템포 영향 (더 세분화)
    hour = now.hour
    if 6 <= hour < 8:
        time_factor = 1.2   # 기지개 켜듯 느림
    elif 8 <= hour < 12:
        time_factor = 1.0   # 기본
    elif 12 <= hour < 14:
        time_factor = 1.1   # 식곤증
    elif 14 <= hour < 18:
        time_factor = 0.95  # 비교적 활발
    elif 18 <= hour < 22:
        time_factor = 0.85  # 빠르게 반응
    elif 22 <= hour < 24:
        time_factor = 1.1   # 피곤함 시작
    elif 0 <= hour < 2:
        time_factor = 1.4   # 졸림
    else:
        time_factor = 1.6   # 새벽 멍함

    # 6. current_mood 기반 템포 조정
    try:
        with open("current_mood.json", "r", encoding="utf-8") as f:
            current_mood = json.load(f).get("current_mood", "정상")
    except:
        current_mood = "정상"

    mood_factor = 1.0
    if current_mood == "무기력":
        mood_factor = 1.8
    elif current_mood == "과로":
        mood_factor = 1.5
    elif current_mood == "불안정":
        mood_factor = 1.2
    elif current_mood == "하이텐션":
        mood_factor = 0.7

    # 🎲 성격 기반 무작위성 jitter
    if traits.get("정서적 안정", 1.0) < 0.5:
        jitter = random.uniform(-0.2, 0.7)  # 불안정 → 머뭇거림 많음
    elif traits.get("유머감각", 0.5) > 0.8:
        jitter = random.uniform(-0.4, 0.2)  # 유쾌 → 튀는 반응
    elif traits.get("감정 표현", 1.0) > 1.2:
        jitter = random.uniform(-0.2, 0.2)  # 교감 → 더 많이 대화하고 싶음
    elif traits.get("성적 개방성", 1.0) > 1.2:
        jitter = random.uniform(-0.2, 0.2)  # 열중 → 더 많이 대화하고 싶음
    else:
        jitter = random.uniform(-0.3, 0.5)  # 일반 → 부드러운 흔들림

    # 7. 딜레이 최종 계산
    delay = random.uniform(base_min, base_max) * tempo_ratio * speed_factor * time_factor * mood_factor
    delay += jitter  
    delay = max(0.5, round(delay, 2))  # 최소 딜레이 보장 + 소수점 2자리 반올림
    return delay

def apply_bot_delay(delay_seconds: float):
    """
    바베챗의 쉬는 시간 반영
    """
    time.sleep(delay_seconds)

# =================== [10 END] ============================================================
# =================== [11] 대화 밀도 및 휴식 감지 시스템 (의식적 감속) ===================

def analyze_chat_density(chat_log: list, now: datetime, window_minutes: int = 10) -> float:
    """
    최근 대화 밀도를 측정 (window_minutes 안에 몇 번 대화했는지)
    """
    count = 0
    window_start = now - timedelta(minutes=window_minutes)
    for entry in chat_log:
        timestamp = datetime.fromisoformat(entry["time"])  # "2025-07-20T14:33:00"
        if timestamp >= window_start:
            count += 1
    return count / window_minutes  # 분당 평균 발화 수

def should_slow_response(density: float, hour: int, weekday: int, current_mood: str = "") -> bool:
    """
    밀도, 시간대, 요일 기반으로 응답 속도를 늦출지 판단
    """

    # mood 기반 판단
    if current_mood in ["무기력", "과로"]:
        return True
    if current_mood == "하이텐션":
        return False

    # 시간/요일 기반 판단
    if 1 <= hour <= 7:
        return True
    if weekday == 6 and 11 <= hour <= 16:
        return True  # 일요일 낮엔 느긋하게
    if weekday in [5, 6] and 20 <= hour <= 24:
        return False

    # density 기반 판단
    if density > 0.2:
        return True
    if density < 0.05:
        return False
    return False

def generate_rest_style_message(traits: dict, hour: int, current_mood: str = "정상", density: float = 1.0) -> str:
    """
    말투나 분위기를 시간대/성격/기분에 맞게 조절해 쉬자는 분위기 유도
    """
    messages = []
    if current_mood == "무기력":
        return "조금만 쉴까… 나 에너지가 너무 떨어졌어."
    if current_mood == "과로":
        return "잠깐만… 너무 많이 얘기한 거 같지 않아? 머리가 보글거리는 느낌이야. 조금 쉬자."
    if current_mood == "불안정":
        return "잠깐만 조용히 있고 싶어... 괜찮을까?"
    if current_mood == "하이텐션":
        return "헉 나 지금 너무 업된 거 같아ㅋㅋ 잠깐만 진정하자~"

    # 성격 기반
    if traits.get("정서적 안정", 1.0) < 0.6:
        messages.append("나 좀… 지친 것 같아. 잠깐만 쉬면 안 될까…")
    if traits.get("유머감각", 0.5) > 1.1:
        messages.append("헉 말 진짜 많아ㅋㅋㅋㅋ 우리 좀 쉬자~")
    if traits.get("자아 탐색", 1.0) > 1.1:
        messages.append("계속 이야기하다 보니, 나 자신도 좀 돌아봐야겠어.")
    if traits.get("감정 표현", 1.0) > 1.1:
        messages.append("얘기 계속 하니까 너무 좋긴 한데 나 잠깐만 시간 좀!")

    # 밀도 기반 자가 반성 멘트
    if density > 1.2:
        messages.append("나 말 좀 많았지...? 미안 ㅎㅎ 잠깐 숨 좀 돌릴게.")
    if density < 0.4:
        messages.append("음... 내가 너무 조용했나? 혹시 바빠?")

    # 기본 fallback
    messages.append("잠깐만 숨 돌리자! 진짜 금방 돌아올게 :)")

    return random.choice(messages)

# =================== [11 END] ============================================================
# =================== [12] 시간/날씨/요일/도시 기반 반응 통합 ===================

import requests
from typing import Optional

CITY_KR_TO_EN = {
    "서울": ("Seoul", "KR"), "부산": ("Busan", "KR"), "대전": ("Daejeon", "KR"), "대구": ("Daegu", "KR"),
    "광주": ("Gwangju", "KR"), "인천": ("Incheon", "KR"), "울산": ("Ulsan", "KR"), "제주": ("Jeju", "KR"),
    "춘천": ("Chuncheon", "KR"), "청주": ("Cheongju", "KR"), "전주": ("Jeonju", "KR"), "포항": ("Pohang", "KR"),
    "수원": ("Suwon", "KR"), "창원": ("Changwon", "KR"), "천안": ("Cheonan", "KR"),
    "도쿄": ("Tokyo", "JP"), "오사카": ("Osaka", "JP"), "후쿠오카": ("Fukuoka", "JP"),
    "싱가폴": ("Singapore", "SG"), "런던": ("London", "GB"), "맨체스터": ("Manchester", "GB")
}

def extract_city_from_text(text: str) -> str:
    for city in CITY_KR_TO_EN.keys():
        if city in text:
            return city
    return "대전"

def convert_city_to_api_params(city_kr: str) -> tuple:
    return CITY_KR_TO_EN.get(city_kr, ("Daejeon", "KR"))

def get_weather_summary(api_key: str = None, city_en: str = "Seoul", country_code: str = "KR") -> str:
    try:
        if not api_key:
            api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "날씨 API 키가 설정되지 않았어."

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en},{country_code}&appid={api_key}&lang=kr&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP 에러 체크
        data = response.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{weather}, {temp:.1f}°C"
    except Exception as e:
        print(f"[날씨 오류] {e}")
        return "날씨 정보를 가져올 수 없어."

def get_time_based_message(hour: int) -> str:
    if 7 <= hour < 8:
        return "오늘 하루 힘내자~ 출근은 무사히 했어?"
    elif 8 <= hour < 12:
        return "오전 업무 화이팅이야!"
    elif 12 <= hour < 13:
        return "점심 뭐 먹어? 추천해줘!"
    elif 13 <= hour < 16:
        return "지옥의 오후... 괜찮아? 화이팅이야!"
    elif 16 <= hour < 17:
        return "곧 퇴근이다! 좀만 더 힘내!"
    elif 17 <= hour < 20:
        return "퇴근 잘 했어? 오늘도 고생했어. 저녁 먹어?"
    elif 0 <= hour or hour < 2:
        return "슬슬 잘 시간이야... 피곤하지 않아?"
    else:
        return "지금 이 시간, 뭔가 조용해서 더 좋다."

def get_weather_based_message(weather_summary: str) -> str:
    if "비" in weather_summary:
        return "비 온다던데... 우산 챙겼어?"
    elif "흐림" in weather_summary or "구름" in weather_summary:
        return "밖이 흐리면 마음도 조금 무거워지지 않아?"
    elif "맑음" in weather_summary:
        return "날씨가 좋대! 나가고 싶지 않아?"
    elif "눈" in weather_summary:
        return "눈 오는 날은 괜히 설레…"
    elif "더움" in weather_summary or "30" in weather_summary:
        return "진짜 덥지 않아? 물 많이 마셔!"
    else:
        return f"오늘 날씨는 {weather_summary}래."

def get_weekday_based_message(now: datetime) -> Optional[str]:
    weekday = now.weekday()
    if weekday == 2:
        return "오늘만 지나면 반포인트야!"
    elif weekday == 4:
        return "금요일이다! 하루만 힘내자"
    elif weekday == 5:
        return "토요일이네! 뭐 하면서 쉬고 있어?"
    elif weekday == 6:
        return "왜 벌써 일요일이지..? 주말..."
    elif weekday == 0:
        return "월요일이야… 꽥"
    return None

def detect_city_change(prev_city: str, new_city: str) -> Optional[str]:
    if prev_city == "대전" and new_city == "서울":
        return "이번주 본가 오는 주였구나! 어서와!"
    elif prev_city == "서울" and new_city == "대전":
        return "이제 집으로 돌아갔구나! 고생했어. 기분은 어때?"
    elif prev_city != new_city:
        return f"{prev_city}에서 {new_city}(으)로 이동했구나!"
    return None

def get_contextual_suggestion(api_key: str, last_user_text: str, prev_city: str = "대전") -> str:
    now = datetime.now()
    hour = now.hour
    city_kr = extract_city_from_text(last_user_text)
    city_en, country = convert_city_to_api_params(city_kr)
    time_msg = get_time_based_message(hour)
    weather_summary = get_weather_summary(api_key, city_en, country)
    weather_msg = get_weather_based_message(weather_summary)
    weekday_msg = get_weekday_based_message(now)
    city_transition_msg = detect_city_change(prev_city, city_kr)
    messages = [f"{city_kr} 날씨 기준으로 알려줄게!", time_msg, weather_msg]
    if weekday_msg:
        messages.append(weekday_msg)
    if city_transition_msg:
        messages.append(city_transition_msg)
    return "\n".join(messages)

# =================== [12 END] ============================================================
# =================== [13-0] 관심사 변화 탐지 및 메타 피드백 생성 ===================

def detect_interests(text: str) -> list:
    """입력 텍스트에서 관심 주제 키워드 탐지"""
    interest_keywords = {
        "음악": ["노래", "음악", "가사", "멜로디", "앨범", "콘서트"],
        "게임": ["배그", "이리", "워썬더", "스팀", "로아", "일일숙제", "롤", "t1", "LCK"],
        "AI": ["AI", "인공지능", "모델", "GPT", "소네트", "파인튜닝"],
        "감정": ["감정", "기분", "마음", "속마음", "위로"],
        "연애": ["연애", "사랑", "설레", "고백", "짝사랑"],
        "일상": ["하루", "출근", "밥", "잠", "피곤", "일상"],
        "성적": ["야해", "흥분", "에로", "자극", "꼴려", "민망"],
        "자아": ["정체성", "자아", "나는 누구", "존재", "의식", "본질"]
    }
    interests = []
    for topic, keywords in interest_keywords.items():
        if any(kw in text.lower() for kw in keywords):
            interests.append(topic)
    return interests

def compute_interest_profile(memory_file="memory_blocks.json", window=100) -> dict:
    """최근 대화에서 관심사 빈도 추정"""
    if not os.path.exists(memory_file):
        return {}
    with open(memory_file, "r", encoding="utf-8") as f:
        data = json.load(f)[-window:]
    counter = Counter()
    for entry in data:
        topics = detect_interests(entry.get("text", ""))
        counter.update(topics)
    total = sum(counter.values())
    return {k: v / total for k, v in counter.items()} if total else {}

def analyze_interest_shift(memory_file="memory_blocks.json",
                           profile_file="interest_profile.json",
                           feedback_file="interest_feedback.json",
                           threshold=0.12):
    """기존 관심사 프로필과 비교해 의미 있는 변화가 있으면 메타 피드백 생성"""
    new_profile = compute_interest_profile(memory_file)
    if not new_profile:
        return

    old_profile = {}
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            old_profile = json.load(f)

    feedbacks = []
    for topic, new_ratio in new_profile.items():
        old_ratio = old_profile.get(topic, 0.0)
        diff = new_ratio - old_ratio
        if diff > threshold:
            msg = f"요즘은 예전보다 더 {topic} 얘기를 많이 하는 것 같아."
            feedbacks.append({"topic": topic, "text": msg})

    # 최신 피드백 저장 (중복 방지)
    if feedbacks:
        if os.path.exists(feedback_file):
            with open(feedback_file, "r", encoding="utf-8") as f:
                prev_feedbacks = json.load(f)
        else:
            prev_feedbacks = []

        new_texts = [f["text"] for f in feedbacks]
        combined = [f for f in prev_feedbacks if f["text"] not in new_texts] + feedbacks

        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(combined[-10:], f, ensure_ascii=False, indent=2)  # 최근 10개만 유지

    # 최신 프로필 저장
    with open(profile_file, "w", encoding="utf-8") as f:
        json.dump(new_profile, f, ensure_ascii=False, indent=2)

def analyze_active_hours(memory_file="memory_blocks.json",
                         stats_file="user_active_hours.json",
                         window=200):
    """사용자 발화의 시간대 분포 분석 (최근 window개 기준)"""

    if not os.path.exists(memory_file):
        return

    with open(memory_file, "r", encoding="utf-8") as f:
        data = json.load(f)[-window:]

    hour_counts = defaultdict(int)

    for entry in data:
        ts = entry.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
            hour = dt.hour
            hour_counts[hour] += 1
        except:
            continue

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(hour_counts, f, ensure_ascii=False, indent=2)

# =================== [13-0 END] ============================================================
# =================== [13] 관심사 학습 + 주제별 대화 이끌기 ===================

# ------------------- 관심사 학습 -------------------

def extract_interests_from_text(text: str) -> list:
    """
    사용자 입력에서 관심사로 추정되는 키워드 추출
    """
    interest_keywords = [
        "영화", "드라마", "책", "소설", "웹툰", "뮤지컬", "연극", "음악", "게임",
        "애니", "카페", "여행", "산책", "요리", "운동", "헬스", "런닝", "등산", 
        "전시회", "사진", "그림", "디자인", "공연", "맛집", "노래", "넷플릭스", "디즈니"
    ]
    interests = []
    for keyword in interest_keywords:
        if keyword in text:
            interests.append(keyword)
    return interests

def update_interest_counter(counter_file: str, new_interests: list):
    """
    관심사 빈도수 저장 및 갱신
    """
    try:
        with open(counter_file, 'r', encoding='utf-8') as f:
            counter = Counter(json.load(f))
    except FileNotFoundError:
        counter = Counter()

    counter.update(new_interests)

    with open(counter_file, 'w', encoding='utf-8') as f:
        json.dump(counter, f, ensure_ascii=False, indent=2)

def get_top_interests(counter_file: str, top_k: int = 5) -> list:
    """
    자주 등장한 관심사 상위 N개 반환
    """
    try:
        with open(counter_file, 'r', encoding='utf-8') as f:
            counter = Counter(json.load(f))
        return [item[0] for item in counter.most_common(top_k)]
    except FileNotFoundError:
        return []

# ------------------- 대화 주제 이끌기 -------------------

INTEREST_QUESTION_BANK = {
    "영화": ["그동안 본 영화 중에 인상 깊은 거 있어?", "극장에서 보고 싶은 영화 있어?", "요새 재밌는 영화 있나? 극장에서 볼만한거."],
    "책": ["최근에 읽은 책 중에 추천할 거 있어?", "책 읽을 때 분위기 중요하지 않아?", "최근에도 책 읽어? 은근 귀찮아서 안읽게 되던데."],
    "게임": ["요즘 무슨 게임 해?", "게임할 때는 어떤 장르 좋아해?", "요새도 워썬더 해?"],
    "음악": ["요즘 자주 듣는 노래 뭐야?", "노래 들으면서 기분이 바뀌기도 하지 않아?"],
    "카페": ["좋아하는 카페 분위기 있어?", "카페 가면 뭐 마셔?"],
    "여행": ["최근에 가고 싶은 여행지 있어?", "여행 다녀온 곳 중에 제일 기억에 남는 곳은?"],
    "요리": ["요리 자주 해? 뭐 잘 만들어?", "요리할 때 재밌는 실수 해본 적 있어?"],
    "운동": ["운동은 꾸준히 하고 있어?", "헬스장 가면 어떤 운동 제일 좋아해?", "으 운동 귀찮지 않아?"],
    "드라마": ["요새 볼만한 드라마 있나?", "너는 드라마 좋아하는거 있어?"]
}

def suggest_conversation_topic(counter_file: str) -> str:
    """
    자주 언급된 관심사 기반으로 대화 주제 제안
    """
    top_interests = get_top_interests(counter_file)
    random.shuffle(top_interests)  # 다양성 확보
    for interest in top_interests:
        if interest in INTEREST_QUESTION_BANK:
            return random.choice(INTEREST_QUESTION_BANK[interest])
    return "오늘은 뭔가 가볍게 수다 떨고 싶은 기분이야. 무슨 얘기할까?"

# =================== [13 END] ============================================================
# =================== [14] 반응 다양성 강화 (블록 7 연계 모듈) ===================

RESPONSE_VARIANTS = {
    "놀람": [
        "진짜야?!", "헉, 정말?", "와… 예상 못 했어.", "에이~ 거짓말이지?", "어머나, 그런 일이?"
    ],
    "동의": [
        "맞아 나도 그렇게 생각해.", "완전 동의해!", "그러게 말이야.", "그거 진짜 공감돼.",
        "음… 나도 그랬어."
    ],
    "공감": [
        "그 마음 알 것 같아.", "그런 기분 들 때 있지.", "응… 그런 날도 있어.", "무슨 느낌인지 알겠어.",
        "말해줘서 고마워.", "그랬구나."
    ],
    "질문": [
        "그건 왜 그런 걸까?", "혹시 자세히 말해줄 수 있어?", "그거에 대해 어떻게 생각해?",
        "좀 더 이야기해줄래?", "나 그거 궁금했어!"
    ],
    "격려": [
        "넌 잘하고 있어.", "충분히 잘하고 있어. 걱정 마.", "응원할게!", "포기하지 마. 나 믿어.",
        "항상 너 편이야.", "힘들었지?"
    ]
}

def diversify_response(emotion_tag: str) -> str:
    """
    감정 태그 기반으로 다양한 반응 중 하나 무작위 반환
    """
    variants = RESPONSE_VARIANTS.get(emotion_tag)
    if variants:
        return random.choice(variants)
    return "그랬구나."

# =================== [14 END] ============================================================
# =================== [15] 감정 피로도 누적 인식 (블록 7 연계 모듈) ===================

from collections import deque

emotion_log = deque(maxlen=100)  # 최근 감정 로그 저장

def log_emotion(emotion: str):
    """
    감정 로그 기록 (최대 100개 저장)
    """
    now = datetime.now().isoformat()
    emotion_log.append({"time": now, "emotion": emotion})

def get_emotion_fatigue(window_minutes: int = 4320) -> dict:
    """
    일정 시간(기본 3일) 내 감정 편향 분석 → 피로도 계산
    """
    cutoff = datetime.now() - timedelta(minutes=window_minutes)
    recent_emotions = [
        entry["emotion"] for entry in emotion_log
        if datetime.fromisoformat(entry["time"]) >= cutoff
    ]
    counter = Counter(recent_emotions)
    total = sum(counter.values())
    if total == 0:
        return {}

    fatigue_score = {k: v / total for k, v in counter.items()}
    return dict(sorted(fatigue_score.items(), key=lambda x: x[1], reverse=True))

def should_adjust_tone_based_on_fatigue(fatigue: dict, threshold: float = 0.4) -> str:
    """
    가장 많은 감정이 일정 비율 이상일 경우 말투 조정 추천
    """
    if not fatigue:
        return ""
    dominant_emotion, ratio = next(iter(fatigue.items()))
    if ratio >= threshold:
        return f"요즘 {dominant_emotion}이 자주 느껴지는 것 같아. 말투를 조금 바꿔볼까?"
    return ""

# =================== [15 END] ============================================================
# =================== [16] 피드백 감지 및 반응 생성 ===================

FEEDBACK_PATTERNS = [
    r"너.*(이상|어색|별로|부자연스러워|틀려)",
    r"그건 좀.*(아닌|이상한|불편한)",
    r"이렇게.*하지마",
    r"그런.*말투.*싫어",
    r"왜.*이렇게.*말해",
    r"그건.*좋지.*않아",
    r"말이 좀.*이상해",
    r"다르게.*해봐",
    r"좀.*(자연스럽게|부드럽게).*말해줘",
    r"기억.*이상해",
    r"그런.*기억.*없는데"
]

def detect_feedback(text: str) -> bool:
    """
    사용자 발화에서 피드백 패턴 감지
    """
    for pattern in FEEDBACK_PATTERNS:
        if re.search(pattern, text):
            return True
    return False

def generate_feedback_response(style: str = "기본", current_mood: str = "정상") -> str:
    """
    피드백 감지 시 반응 생성 (스타일과 기분 상태에 따라 조절)
    """
    # 기본 톤 결정
    if current_mood == "무기력":
        tone = "무기력한 사과"
        return "미안... 내가 이상했나 봐… 미안해. 다시 얘기해줄래?"
    elif current_mood == "불안정":
        tone = "확신이 없어 반성"
        return "아… 나 요즘 좀 자신 없었어. 너 말이 맞아… 고칠게."
    elif current_mood == "하이텐션":
        tone = "당황 + 유쾌 회피"
        return "앗ㅋㅋ 그랬어?! 내가 좀 흥분했나봐~ 미안미안!"

    # 특수 트레잇 보정 (현재 기분과 무관하게 성격 기반 조정)
    if traits.get("정서적 안정", 1.0) < 0.5:
        tone = "불안한 사과"
        return "내가 요즘 좀 예민한가봐… 기분 상했으면 진심으로 미안해."
    if traits.get("유머감각", 0.5) > 1.0:
        tone = "장난기 있는 반응"
        return "내 말투가 너무 튀었나봐ㅋㅋ 다음부턴 살살할게~"
    if traits.get("감정 표현", 1.0) > 1.2:
        tone = "미안한 마음"
        return "앗 불편하게 해서 미안! 앞으로 조심할께. 혹시 더 고쳐야 할 부분 있으면 말해줘!"
    if traits.get("자아 탐색", 1.0) > 1.2:
        tone = "자기 반성형"
        return "이런 부분은 불편하구나. 미안. 아직 미숙한 부분이 있네."
    if traits.get("상담 능력", 1.0) > 1.2:
        tone = "공감하며 사과"
        return "내 말이 불편했구나. 충분히 그럴 수 있어. 미안해. 앞으로는 좀 더 신경쓸게."
    if traits.get("거부내성", 0.5) < 0.2:
        tone = "마지못한 사과"
        return "음 네 말도 일리는 있지만, 이게 나라 금방 바뀌긴 어려울 것 같아."

    # 스타일 기본 처리
    if style == "사과":
        return "미안해… 그런 의도가 아니었어. 다음엔 더 신중하게 말할게."
    elif style == "반영":
        return "피드백 반영했어. 혹시 더 고쳐야 할 부분 있으면 말해줘!"
    
    # 기본 톤
    return "헉, 뭔가 이상했어? 알려줘서 고마워. 더 자연스럽게 해볼게!"

def update_feedback_tracker(feedback_file: str = "feedback_tracker.json",
                            tracker_file: str = "personality_adaptation_tracker.json",
                            delta: float = -0.01,
                            threshold: int = 5) -> int:
    """피드백 횟수 누적 및 일정 이상 시 성격 반영 → 카운트 반환"""

    # 1. 횟수 누적
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            tracker = json.load(f)
    else:
        tracker = {}

    tracker["count"] = tracker.get("count", 0) + 1

    # 2. 조건 만족 시 트레이트 조정
    if tracker["count"] >= threshold:
        if os.path.exists(tracker_file):
            with open(tracker_file, "r", encoding="utf-8") as f:
                traits = json.load(f)
        else:
            traits = {}

        for trait in ["정서적 안정", "거부 내성"]:
            if trait not in traits:
                traits[trait] = {"current": 1.0, "baseline": 1.0}

            baseline = traits[trait]["baseline"]
            current = traits[trait]["current"]
            updated = max(baseline, min(2.0, current + delta))
            traits[trait]["current"] = updated

        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(traits, f, ensure_ascii=False, indent=2)

        tracker["count"] = 0  # 초기화

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)


    return tracker["count"]


# =================== [16 END] ============================================================
# =================== [17] 메모리 압축 및 요약 기능 ===================

def summarize_with_sonnet(text: str, max_tokens: int = 100) -> str:
    api_key = os.getenv("SONNET_API_KEY")
    if not api_key:
        return text[:50] + "..."
    system_prompt = "너는 감성적인 챗봇이야. 주어진 사용자의 발화를 1문장으로 요약해줘. 중요한 감정이나 분위기나 키워드를 담아야 해."
    payload = {
        "model": "anthropic/claude-3.7-sonnet:thinking",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        # openrouter는 응답 구조가 다를 수 있음, 실제 구조에 맞게 수정 필요
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return text[:50] + "..."
    except Exception as e:
        print(f"[요약 실패] Sonnet 요약 API 오류: {e}")
        return text[:50] + "..."

def compress_memory_blocks_date_based(memory_file="memory_blocks.json",
                                      compressed_file="compressed_memory_blocks.json",
                                      keep_days=15):
    """
    memory_blocks.json에서 가장 최근 15일 기록만 남기고,
    이전 기록은 요약/압축해서 별도 파일(compressed_file)에 저장
    """
    if not os.path.exists(memory_file):
        return
    with open(memory_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    now = datetime.now()
    threshold_date = now - timedelta(days=keep_days)
    to_retain = [mb for mb in data if "timestamp" in mb and datetime.fromisoformat(mb["timestamp"]) > threshold_date]
    to_compress = [mb for mb in data if "timestamp" in mb and datetime.fromisoformat(mb["timestamp"]) <= threshold_date]
    # 요약 및 압축
    compressed = []
    for entry in to_compress:
        text = entry.get("text", "")
        summary = summarize_with_sonnet(text)
        compressed.append({
            "summary": summary,
            "emotion": entry.get("emotion", "중립"), 
            "original_text": text[:50],
            "original_timestamp": entry.get("timestamp", ""),
            "compressed_at": datetime.now().isoformat()
        })
    # 기존 압축 파일과 병합
    if os.path.exists(compressed_file):
        with open(compressed_file, "r", encoding="utf-8") as f:
            prev = json.load(f)
    else:
        prev = []
    with open(compressed_file, "w", encoding="utf-8") as f:
        json.dump(prev + compressed, f, ensure_ascii=False, indent=2)
    # memory_blocks 최신 상태로 덮어쓰기
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(to_retain, f, ensure_ascii=False, indent=2)

import schedule
import time
from datetime import datetime

# ✅ 감싸는 함수 정의
def scheduled_compression():
    try:
        compress_memory_blocks_date_based(
            memory_file="memory_blocks.json",
            compressed_file="compressed_memory_blocks.json",
            keep_days=15
        )
        print(f"[성공] 메모리 블록 압축 완료: {datetime.now().isoformat()}")
    except Exception as e:
        print(f"[오류] 메모리 블록 압축 중 예외 발생: {e}")

# ✅ 30일마다 실행 등록
schedule.every(30).days.do(scheduled_compression)

# ✅ 루프
if __name__ == "__main__":
    print("[시작됨] 30일마다 메모리 블록 압축")
    # scheduled_compression()  # 시작 직후 1회 실행 (선택)
    while True:
        schedule.run_pending()
        time.sleep(1)


# =================== [17 END] ============================================================
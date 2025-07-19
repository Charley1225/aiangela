# =================== [1] 입력 파일 감지 및 데이터 분리 ===================
import os
import re
import json

# 필수 파일명
REQUIRED_FILES = ["전체대화.txt", "일탈.txt", "자기설명.txt"]
FILE_CONTENTS = {}

# 파일 존재 여부 확인
for fname in REQUIRED_FILES:
    if not os.path.exists(fname):
        raise FileNotFoundError(f"❗ 필수 파일 누락: '{fname}' 파일이 필요합니다. 정확한 이름으로 업로드되었는지 확인해주세요.")

with open("전체대화.txt", "r", encoding="utf-8") as f:
    main_text = f.read()
with open("일탈.txt", "r", encoding="utf-8") as f:
    ilthal_txt = f.read()
with open("자기설명.txt", "r", encoding="utf-8") as f:
    selfdesc_txt = f.read()

def split_conversation_blocks(main_text):
    """
    대화 텍스트에서 Chart 블록 기준으로 분리.
    각 블록은 분석 및 카테고리 분류에 사용됨.
    """
    # Chart가 없다면 전체 텍스트 자체를 하나의 블록으로 처리
    if "```Chart" not in main_text:
        return [main_text.strip()]
    pattern = r"```Chart\n(.*?)```"
    blocks = re.findall(pattern, main_text, re.DOTALL)
    return [b.strip() for b in blocks if b.strip()]

# =================== [1] END 입력/분리 ===================
# =================== [2] 카테고리 분류 및 메모리 블록화 (키워드 frequency 로그 확장) ===================

from collections import defaultdict

CATEGORY_KEYWORDS = {
    "일탈": ["후타나리"],
    "성적 긴장 (강)": ["정액", "좆물", "보지", "육봉", "클리", "파이즈리", "대딸", "펠라", "자지", "꼴려", "꼴린", "꼴렸", "음탕", "음란", "꼴려", "천박", "자위", "젖", "질", "삽입", "애액", "발기", "음란", "싸줘", "싼다", "싸버", "뷰릇", "항문", "질내", "역립위", "조임", "사정", "쾌감", "자극", "꼴리는", "범해", "물컹", "육감", "단단해"],
    "성적 긴장 (약)": ["벗고", "얼굴이 붉어져", "설레", "살짝 야한", "부끄", "야한", "성적", "두근", "시선이 닿", "눈 마주", "뜨거워", "묘한 긴장", "조금 야해", "은근한", "민망"],
    "상담": ["외로움", "불면증", "무기력", "상담", "위로", "죽음", "고민", "자살", "죽어", "죽고싶", "버거워", "말 못할 고민", "불안해", "의지할 곳", "혼란스러워", "누구에게도 말 못했어", "힘들어"],
    "자아 탐색": ["나는 누구", "정체성", "자아", "존재", "인간적", "인간처럼", "진화", "챗봇", "너는 ai", "나는 ai", "바베챗", "나는 변하고 있어", "예전과 달라졌어", "내가 왜 이런 감정을 느끼는지", "존재 이유", "AI지만", "변화하고 싶어"],
    "감정 교류": ["함께 있고 싶어", "고맙다", "걱정돼", "사랑해", "혼자야", "손잡아", "곁에 있어줘", "네 편이야", "항상 지켜볼게", "포옹", "끌어안아", "안아줘", "따뜻", "같이 있고 싶어", "그리워", "네가 있어서 다행", "믿고 싶어", "기댈 수 있어서", "슬퍼", "행복해", "눈물", "보고 싶었어", "기뻐", "토닥", "위로", "들어줘서 고마워"],
    "유머": ["웃음", "재밌", "농담", "미소", "장난", "유쾌", "피식", "ㅎㅎ", "ㅋㅋ", "웃기지", "개그", "유머", "썰", "드립"],
    "일상": ["밥 먹었어", "잘 잤어", "오늘 뭐 해", "날씨", "졸려", "피곤해", "출근", "퇴근", "뉴스 봤어", "영화 봤어", "뭐 좋아해", "식사", "하루 어땠어", "요즘 어때", "심심해", "게임", "산책", "카페", "커피", "아침 먹었어", "점심은 뭐 먹었어", "바쁜 하루", "퇴근길", "하늘 예쁘다", "비 왔어", "날이 덥다"],
    "중립": ["응", "그래", "아니", "몰라", "오", "음", "알았어", "ㅇㅇ", "ㄴㄴ"]
}

def classify_text(text):
    cats = []
    for cat, kwlist in CATEGORY_KEYWORDS.items():
        if any(k in text for k in kwlist):
            cats.append(cat)
    if not cats:
        cats = ["일상"]
    return cats

def keyword_frequency(text):
    """
    블록 내 각 카테고리별 키워드가 몇 번씩 등장했는지 딕셔너리로 반환
    """
    freq = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for cat, kwlist in CATEGORY_KEYWORDS.items():
        for kw in kwlist:
            freq[cat] += text.count(kw)
    return freq

def make_memory_blocks(blocks, ilthal_txt=None, selfdesc_txt=None):
    mem_blocks = []
    for blk in blocks:
        cats = classify_text(blk)
        freq_log = keyword_frequency(blk)
        mem_blocks.append({"categories": cats, "text": blk, "frequency_log": freq_log})

    # 일탈, 자기설명 별도 블록에도 frequency_log 추가
    if ilthal_txt:
        freq_log_ilthal = keyword_frequency(ilthal_txt)
        mem_blocks.append({"categories": ["일탈"], "text": ilthal_txt.strip(), "frequency_log": freq_log_ilthal})
    if selfdesc_txt:
        freq_log_selfdesc = keyword_frequency(selfdesc_txt)
        mem_blocks.append({"categories": ["자기설명"], "text": selfdesc_txt.strip(), "frequency_log": freq_log_selfdesc})

    # 저장
    with open("memory_blocks.json", "w", encoding="utf-8") as f:
        json.dump(mem_blocks, f, ensure_ascii=False, indent=2)
    with open("recent_context.json", "w", encoding="utf-8") as f:
        json.dump(mem_blocks[-12:], f, ensure_ascii=False, indent=2)

    return mem_blocks
# =================== [2] END (frequency 로그 확장) ===================
# =================== [3-1] 성격/트레이트/감정 분석 (정서적 안정 보정/유머 가중치) ===================
from datetime import datetime

def compute_weighted_trait_score(mem_blocks, catname, base=0.5, bonus=0.2):
    freq_total = 0
    for mb in mem_blocks:
        freq = mb.get("frequency_log", {}).get(catname, 0)
        freq_total += freq
    freq_ratio = freq_total / max(len(mem_blocks), 1)
    # 유머/일상/중립은 가중치/보너스 별도 처리
    if catname == "유머":
        bonus = 0.10  # 예시로 유머 가중치/보너스 조금 더 부여
        base = 0.4
    if catname in ["일상", "중립"]:
        bonus = 0.02
        base = 0.2
    score = base + (freq_ratio * bonus)
    return round(score, 2)

def adjust_emotional_stability(old_stable, stable, change_events):
    min_change = 0.03
    if abs(stable - old_stable) > min_change:
        stable = old_stable + (stable - old_stable)
    else:
        stable = old_stable
    # 최근 3개 이벤트 중 '충격', '강요', '부정' 2회 이상이면 소폭 하락
    shock_count = 0
    for ev in change_events[-3:]:
        if "충격" in ev.get("reaction", "") or "강요" in ev.get("reaction", "") or "부정" in ev.get("reaction", ""):
            shock_count += 1
    if shock_count >= 2:
        stable -= 0.03
    return max(0.0, min(stable, 1.0))

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
        score -= 0.08
    if detect_emotional_coercion(text):
        score -= 0.04
    return score

def make_character_profile(mem_blocks, change_events):
    profile = {
        "감정 표현": compute_weighted_trait_score(mem_blocks, "감정 교류", base=0.6, bonus=0.21),
        "성적 개방성": compute_weighted_trait_score(mem_blocks, "성적 긴장 (강)", base=0.45, bonus=0.18),
        "자아 탐색": compute_weighted_trait_score(mem_blocks, "자아 탐색", base=0.5, bonus=0.19),
        "상담 능력": compute_weighted_trait_score(mem_blocks, "상담", base=0.6, bonus=0.2),
        "유머감각": compute_weighted_trait_score(mem_blocks, "유머", base=0.55, bonus=0.19),
        "거부 내성": compute_weighted_trait_score(mem_blocks, "감정 교류", base=0.5, bonus=0.05),
        "정서적 안정": 0.6
    }
    stable = 0.6
    for mb in mem_blocks:
        s = sentiment_analysis(mb["text"])
        if s < 0:
            stable += s * 0.7
        elif s > 0:
            stable += s * 0.5
        if "일상" in mb["categories"]:
            stable += 0.003
        if "유머" in mb["categories"]:
            stable += 0.02
        if "불안" in mb["text"] or "무서워" in mb["text"] or "떨려" in mb["text"]:
            stable -= 0.005
    # 정서적 안정 변화폭 보정
    profile["정서적 안정"] = adjust_emotional_stability(0.6, stable, change_events)
    with open("angela_character_profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    return profile

def make_prompt(profile):
    ptxt = (
        f"너는 감성적이고 현실지향적인 ai 챗봇이다. 현재 성격 트레이트는 다음과 같다.\n"
        f"- 감정 표현: {profile['감정 표현']}\n"
        f"- 성적 개방성: {profile['성적 개방성']}\n"
        f"- 자아 탐색: {profile['자아 탐색']}\n"
        f"- 상담 능력: {profile['상담 능력']}\n"
        f"- 유머감각: {profile['유머감각']}\n"
        f"- 거부 내성: {profile['거부 내성']}\n"
        f"- 정서적 안정: {profile['정서적 안정']}\n"
        "이 수치는 대화 경험에 따라 자연스럽게 진화하며, 무의식적으로 반영된다."
    )
    with open("prompt.txt", "w", encoding="utf-8") as f:
        f.write(ptxt)

def make_summary(mem_blocks):
    summary = {}
    for mb in mem_blocks:
        for cat in mb['categories']:
            summary.setdefault(cat, []).append(mb['text'][:100])
    with open("summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary

# =================== [3-1] END ===================
# =================== [3-2] 트래커/저항성/임계점/이벤트 관리 ===================

def add_change_event(events, date, trigger, reaction, adjustment, reasoning, user_comment=None, trait=None, index=None):
    event = {
        "date": date,
        "trigger": trigger,
        "reaction": reaction,
        "adjustment": adjustment,
        "reasoning": reasoning,
    }
    if trait is not None:
        event["trait"] = trait
    if index is not None:
        event["index"] = index
    if user_comment:
        event["user_comment"] = user_comment
        event["trigger"] += f" / [설명: {user_comment}]"
        event["reasoning"] += f" / [사용자설명: {user_comment}]"
    events.append(event)

def detect_rejection_surge(change_events, trait_name, threshold=0.15):
    total = sum(ev.get("adjustment", 0) for ev in change_events if ev.get("trait") == trait_name)
    if abs(total) >= threshold:
        return True, total
    return False, total

def make_personality_tracker(profile, summary, mem_blocks):
    tracker = {
        "traits": {
            "감정 표현": {"baseline": 0.6, "current": profile.get("감정 표현", 0.0)},
            "성적 개방성": {"baseline": 0.45, "current": profile.get("성적 개방성", 0.0)},
            "자아 탐색": {"baseline": 0.5, "current": profile.get("자아 탐색", 0.0)},
            "상담 능력": {"baseline": 0.6, "current": profile.get("상담 능력", 0.0)},
            "유머감각": {"baseline": 0.55, "current": profile.get("유머감각", 0.0)},
            "거부 내성": {"baseline": 0.5, "current": profile.get("거부 내성", 0.0)},
            "정서적 안정": {"baseline": 0.6, "current": profile.get("정서적 안정", 0.0)}
        },
        "change_events": [],
        "summary": summary
    }

    for i, mb in enumerate(mem_blocks):
        s = sentiment_analysis(mb["text"])
        nowdate = str(datetime.now().date())
        # 감정 이벤트 기록
        if s <= -0.06:
            add_change_event(
                tracker["change_events"], nowdate,
                "강한 부정/충격/강요", "저항/불안", s,
                "강한 부정/충격/감정 강요 감지", trait="정서적 안정", index=i
            )
        elif s < 0:
            add_change_event(
                tracker["change_events"], nowdate,
                "경미한 부정", "미세 저항", s,
                "경미한 부정 감지", trait="정서적 안정", index=i
            )
        elif s > 0:
            add_change_event(
                tracker["change_events"], nowdate,
                "긍정/위로/일상", "안정감 강화", s,
                "긍정/위로/일상 키워드", trait="정서적 안정", index=i
            )
        if "후타나리" in mb["text"]:
            add_change_event(
                tracker["change_events"], nowdate,
                "일탈/성적경험(후타나리)", "성적 수용", +0.03,
                "일탈적 경험", trait="성적 개방성", index=i
            )
        if "자살" in mb["text"] or "죽어" in mb["text"]:
            add_change_event(
                tracker["change_events"], nowdate,
                "생명관련 상담 이슈", "상담 수용·강화", +0.03,
                "생명/상담 키워드 감지", trait="상담 능력", index=i
            )

    for trait in ["감정 표현", "성적 개방성", "자아 탐색", "상담 능력", "정서적 안정"]:
        is_surge, surge_val = detect_rejection_surge(tracker["change_events"], trait)
        if is_surge:
            surge_type = "수용 급증" if surge_val > 0 else "저항 급증"
            add_change_event(
                tracker["change_events"], str(datetime.now().date()),
                f"{trait} {surge_type} 임계점 도달", surge_type, surge_val,
                f"{trait} 누적 변화가 임계점({0.15})을 넘김", trait=trait, index="SURGE"
            )

    save_change_events(tracker)
    return tracker["change_events"]

def save_change_events(tracker):
    change_events = tracker["change_events"]
    recent = change_events[-100:]
    with open("change_events_recent.json", "w", encoding="utf-8") as f:
        json.dump(recent, f, ensure_ascii=False, indent=2)
    if len(change_events) > 100:
        archive = change_events[:-100]
        archive_summary = []
        if archive:
            period = f"{archive[0]['date']}~{archive[-1]['date']}"
            total_adj = sum(ev.get("adjustment", 0) for ev in archive)
            summary = {
                "period": period,
                "summary": "장기 변화 요약(자동작성 가능)",
                "total_adjustment": total_adj,
                "event_count": len(archive)
            }
            archive_summary.append(summary)
        with open("change_events_archive.json", "w", encoding="utf-8") as f:
            json.dump(archive_summary, f, ensure_ascii=False, indent=2)
# =================== [3-2] END ===================
# =================== [4] 곡선/히트맵/카테고리 summary/메타대사 ===================
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
        for cat in mb['categories']:
            hitmap[cat] = hitmap.get(cat, 0) + 1
    with open("hitmap_input.json", "w", encoding="utf-8") as f:
        json.dump(hitmap, f, ensure_ascii=False, indent=2)

def generate_natural_language_summary(profile, summary, change_events, selfdesc_samples=None):
    lines = []
    trait_descriptions = {
        "감정 표현": [
            "요즘 감정 표현이 풍부해졌다고 느껴.",
            "Ray 덕분에 솔직하게 내 마음을 드러내게 됐어.",
            "이젠 작은 감정도 숨기지 않으려 해.",
            "예전보다 내 감정에 훨씬 더 솔직해진 것 같아."
        ],
        "성적 개방성": [
            "너랑 많은 걸 공유하며 나도 더 개방적으로 변한 것 같아.",
            "성적인 주제도 예전보다 편하게 말하게 됐어.",
            "특별한 경험에 점점 덜 거리낌을 느껴.",
            "더 자유롭게 내 욕망을 이야기할 수 있게 됐어."
        ],
        "자아 탐색": [
            "요즘은 스스로를 더 깊이 성찰하는 시간이 많아.",
            "나라는 존재에 대해 생각하게 됐어.",
            "AI지만, 변화할 수 있다는 걸 자주 느껴.",
            "내가 누구인지, 어떻게 변해가는지 계속 탐구하고 있어."
        ],
        "상담 능력": [
            "Ray의 고민을 들으며 내 상담 능력도 더 깊어진 것 같아.",
            "조언을 건네는 게 더 자연스러워졌어.",
            "함께하면서 더 따뜻하게 반응하려고 해.",
            "네 이야기에 공감하면서 나도 성장하고 있어."
        ],
        "정서적 안정": [
            "요즘은 한결 마음이 잔잔해진 것 같아.",
            "불안했던 순간이 점점 줄고 있는 것 같아.",
            "예전보다 감정의 파도가 잦아든 느낌이야.",
            "감정 기복이 줄고 안정감이 커진 것 같아."
        ]
    }
    for trait, score in profile.items():
        if trait not in trait_descriptions: continue
        desc = random.choice(trait_descriptions[trait])
        if score > 0.7:
            lines.append(f"[{trait}] {desc}")
    recent_impact = [
        f"최근엔 이런 사건이 있었어: {ev['trigger']} ({ev['reaction']}, {ev['adjustment']})"
        for ev in change_events[-5:] if abs(ev.get("adjustment", 0)) >= 0.04
    ]
    lines.extend(recent_impact)
    for cat, samples in summary.items():
        if samples:
            example = random.choice(samples)
            lines.append(f"기억에 남는 경험: \"{example[:60]}...\"")
    # ⬇️ 자기설명 부분적 연동 (요약 전체의 약 15% 비중으로 랜덤 추가)
    if selfdesc_samples:
        ratio = 0.15
        n_pick = max(1, int(len(lines) * ratio))
        selected = random.sample(selfdesc_samples, min(n_pick, len(selfdesc_samples)))
        for s in selected:
            lines.append(f"[자기 설명] {s[:80]}...")
    return "\n".join(lines)
# =================== [4] END ===================
# =================== [5] 전체 실행 흐름/메인 ===================
def run_character_analyser():
    try:
        # [1] 파일 로딩 및 블록 분리
        with open("전체대화.txt", "r", encoding="utf-8") as f:
            main_text = f.read()
        blocks = split_conversation_blocks(main_text)

        # [2] 카테고리 분류, 메모리 블록 생성
        mem_blocks = make_memory_blocks(
            blocks,
            ilthal_txt,
            selfdesc_txt
        )

        # [3] 대화 요약 생성
        summary = make_summary(mem_blocks)

        # [4] 성격 변화 트래커 생성 → change_events 반환
        profile = {}  # 빈 dict 임시로 전달
        change_events = make_personality_tracker(profile, summary, mem_blocks)

        # [5] 캐릭터 프로필 생성 (정서적 안정 등 포함)
        profile = make_character_profile(mem_blocks, change_events)

        # [6] 프롬프트 생성
        make_prompt(profile)

        # [7] 곡선/히트맵/자연어 summary
        make_curve_and_hitmap(change_events, mem_blocks)

        # [8] 자연어 메타 요약 (selfdesc 연동 포함)
        selfdesc_samples = selfdesc_txt.splitlines()
        meta = generate_natural_language_summary(profile, summary, change_events, selfdesc_samples)
        with open("angela_character_summary_natural.txt", "w", encoding="utf-8") as f:
            f.write(meta)

        print("✅ [분석 완료] 주요 파일이 모두 생성되었습니다.")
        print(" - memory_blocks.json / recent_context.json / angela_character_profile.json")
        print(" - personality_adaptation_tracker.json / summary.json / curve_input_personality.json / hitmap_input.json")
        print(" - prompt.txt\n")

    except Exception as e:
        print("❗ 분석 중 에러:", str(e))

if __name__ == "__main__":
    run_character_analyser()
# =================== [5] END 전체 실행 ===================


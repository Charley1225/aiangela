
import os
import sys

def check_required_files():
    required_main = "전체대화.txt"
    optional_files = {
        "일탈.txt": "성적 일탈 분석 강화를 위해 사용됩니다.",
        "자기설명.txt": "프롬프트 보정 및 캐릭터 자기인식 참고용입니다."
    }

    if not os.path.exists(required_main):
        print(f"❌ 필수 파일 '{required_main}' 이(가) 존재하지 않습니다. 분석을 중단합니다.")
        sys.exit(1)
    else:
        print(f"✅ '{required_main}' 파일을 찾았습니다.")

    for file, description in optional_files.items():
        if not os.path.exists(file):
            print(f"⚠️ 선택 파일 '{file}' 이(가) 없습니다. {description} 있으면 업로드하고, 없으면 무시하고 계속 진행해주세요.")
        else:
            print(f"✅ 선택 파일 '{file}' 이(가) 확인되었습니다.")

def main():
    print("📊 통합 분석기 실행 준비 중...")
    check_required_files()
    # 이후 여기에 분석 메인 로직 연결
    print("✅ 파일 확인 완료. 분석을 시작합니다...")

if __name__ == "__main__":
    main()

"""패션디자인 퀴즈 게임의 시작점."""
from input_helpers import read_number


def main():
    try:
        while True:
            print("\n패션디자인 퀴즈 게임에 오신 것을 환영합니다!")
            print("1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 점수 확인\n5. 종료")
            choice = read_number("메뉴 번호를 선택하세요 (1~5): ", 1, 5)
            if choice == 5:
                print("게임을 종료합니다.")
                break
            print("선택한 기능을 준비 중입니다.")
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 안전하게 종료합니다.")


if __name__ == "__main__":
    main()

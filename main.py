"""터미널에서 python3 main.py로 실행한다."""
from game import QuizGame


def main():
    try:
        QuizGame().run()
    except (KeyboardInterrupt, EOFError):
        print("\n시작 중 입력이 중단되어 종료합니다.")


if __name__ == "__main__":
    main()

"""메뉴와 게임 진행을 관리하는 QuizGame 클래스."""
from defaults import default_quizzes
from input_helpers import read_number, read_text
from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.quizzes = default_quizzes()
        self.best_score = None

    def show_menu(self):
        print("\n패션디자인 퀴즈 게임에 오신 것을 환영합니다!")
        print("1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 점수 확인\n5. 종료")

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = read_number("메뉴 번호를 선택하세요 (1~5): ", 1, 5)
                if choice == 5:
                    break
                actions = {1: self.play, 2: self.add_quiz,
                           3: self.list_quizzes, 4: self.show_score}
                actions[choice]()
        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되었습니다. 안전하게 종료합니다.")
        finally:
            self.save_state()
            print("게임을 종료합니다.")

    def play(self):
        print("퀴즈 풀기를 준비 중입니다.")

    def add_quiz(self):
        print("퀴즈 추가를 준비 중입니다.")

    def list_quizzes(self):
        print("퀴즈 목록을 준비 중입니다.")

    def show_score(self):
        print("점수 확인을 준비 중입니다.")

    def save_state(self):
        pass

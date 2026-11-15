"""메뉴와 게임 진행을 관리하는 QuizGame 클래스."""
import json
import os
from pathlib import Path
import tempfile

from defaults import default_quizzes
from input_helpers import read_number, read_text
from quiz import Quiz


class QuizGame:
    def __init__(self, state_path=None):
        # 현재 터미널 위치와 관계없이 프로젝트 루트에 저장한다.
        self.state_path = (Path(state_path) if state_path is not None
                           else Path(__file__).resolve().parent / "state.json")
        self.quizzes = default_quizzes()
        self.best_score = None
        self.load_state()

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
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
            return
        correct = 0
        total = len(self.quizzes)
        print(f"\n퀴즈를 시작합니다! 총 {total}문제")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[문제 {number}/{total}]")
            quiz.display()
            answer = read_number("정답 번호 (1~4): ", 1, 4)
            if quiz.check_answer(answer):
                correct += 1
                print("정답입니다!")
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")
        score = round(correct / total * 100)
        print(f"\n결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        self.update_best_score(score)

    def update_best_score(self, score):
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("새로운 최고 점수입니다!")
        self.save_state()

    def add_quiz(self):
        print("\n새로운 퀴즈를 추가합니다.")
        question = read_text("문제를 입력하세요: ")
        choices = [read_text(f"선택지 {number}: ") for number in range(1, 5)]
        answer = read_number("정답 번호 (1~4): ", 1, 4)
        # 모든 입력이 끝난 뒤 추가하므로 입력 중단 시 불완전한 문제가 남지 않는다.
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_state():
            print("퀴즈가 추가되고 저장되었습니다.")
        else:
            print("퀴즈가 메모리에 추가되었습니다. 파일 저장은 실패했습니다.")

    def list_quizzes(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")

    def show_score(self):
        if self.best_score is None:
            print("아직 완료한 퀴즈가 없습니다. 먼저 퀴즈를 풀어 보세요.")
        else:
            print(f"최고 점수: {self.best_score}점 (100점 만점)")

    def load_state(self):
        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or not isinstance(data.get("quizzes"), list):
                raise ValueError("quizzes 목록이 필요합니다.")
            score = data["best_score"]
            if score is not None and (type(score) is not int or not 0 <= score <= 100):
                raise ValueError("best_score는 null 또는 0~100 정수여야 합니다.")
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
        except FileNotFoundError:
            print("저장 파일이 없어 기본 퀴즈로 시작합니다.")
        except (ValueError, KeyError, TypeError, UnicodeError) as error:
            print(f"저장 파일이 손상되었습니다. 기본 데이터로 복구합니다. ({error})")
        except OSError as error:
            print(f"저장 파일을 읽을 수 없어 기본 데이터로 시작합니다. ({error})")
        else:
            self.quizzes = quizzes
            self.best_score = score
            print(f"저장된 데이터를 불러왔습니다. 퀴즈 {len(quizzes)}개")

    def save_state(self):
        temporary_path = None
        try:
            data = {"quizzes": [quiz.to_dict() for quiz in self.quizzes],
                    "best_score": self.best_score}
            # 같은 폴더의 임시 파일을 완성한 뒤 교체하여 기존 파일 손상을 줄인다.
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                             dir=self.state_path.parent,
                                             prefix=".state-", suffix=".tmp",
                                             delete=False) as file:
                temporary_path = Path(file.name)
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            temporary_path.replace(self.state_path)
            return True
        except OSError as error:
            print(f"저장하지 못했습니다. 이번 변경은 재실행 시 사라질 수 있습니다. ({error})")
            return False
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass

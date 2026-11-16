"""메뉴, 퀴즈 진행, 보너스 기능과 파일 저장을 관리한다."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import random
import tempfile

from defaults import default_quizzes
from input_helpers import read_number, read_text
from quiz import Quiz

HINT_PENALTY = 10
KOREA_TIME = timezone(timedelta(hours=9))


class QuizGame:
    def __init__(self, state_path=None):
        self.state_path = (Path(state_path) if state_path is not None
                           else Path(__file__).resolve().parent / "state.json")
        self.quizzes = default_quizzes()
        self.best_score = None
        self.history = []
        self.load_state()

    def show_menu(self):
        print("\n패션디자인 퀴즈 게임에 오신 것을 환영합니다!")
        print("1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 점수 확인\n5. 종료")
        print("6. 퀴즈 삭제\n7. 점수 기록")

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = read_number("메뉴 번호를 선택하세요 (1~7): ", 1, 7)
                if choice == 5:
                    break
                actions = {1: self.play, 2: self.add_quiz, 3: self.list_quizzes,
                           4: self.show_score, 6: self.delete_quiz, 7: self.show_history}
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
        total = read_number(f"풀 문제 수 (1~{len(self.quizzes)}): ", 1, len(self.quizzes))
        # 원래 목록은 바꾸지 않고, 중복 없이 무작위로 선택·정렬한다.
        selected = random.sample(self.quizzes, total)
        correct = 0
        hints_used = 0
        print(f"\n퀴즈를 시작합니다! 총 {total}문제 (랜덤 출제)")
        print(f"힌트는 0번: 문제당 한 번, 최종 점수에서 {HINT_PENALTY}점 차감")
        for number, quiz in enumerate(selected, start=1):
            print(f"\n[문제 {number}/{total}]")
            quiz.display()
            used_hint = False
            while True:
                answer = read_number("정답 번호 (1~4, 힌트 0): ", 0, 4)
                if answer != 0:
                    break
                if used_hint:
                    print("이미 이 문제의 힌트를 사용했습니다. 추가 감점은 없습니다.")
                else:
                    used_hint = True
                    hints_used += 1
                    quiz.show_hint()
                    print(f"최종 점수에서 {HINT_PENALTY}점 차감됩니다.")
            if quiz.check_answer(answer):
                correct += 1
                print("정답입니다!")
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")
        base_score = round(correct / total * 100)
        penalty = hints_used * HINT_PENALTY
        score = max(0, base_score - penalty)
        print(f"\n결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        print(f"기본 점수 {base_score}점 - 힌트 감점 {penalty}점 (최저 0점)")
        self.history.append({
            "played_at": datetime.now(KOREA_TIME).isoformat(timespec="seconds"),
            "total": total, "correct": correct, "hints_used": hints_used, "score": score,
        })
        # 완료된 회차만 최고 점수와 기록을 함께 저장한다.
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
        hint = input("힌트 (생략하려면 Enter): ").strip()
        self.quizzes.append(Quiz(question, choices, answer, hint))
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

    def delete_quiz(self):
        if not self.quizzes:
            print("삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        number = read_number(f"삭제할 문제 번호 (취소 0, 1~{len(self.quizzes)}): ",
                             0, len(self.quizzes))
        if number == 0:
            print("삭제를 취소했습니다.")
            return
        quiz = self.quizzes[number - 1]
        print(f"삭제 대상: {quiz.question}")
        confirmation = read_number("정말 삭제할까요? (1: 삭제, 2: 취소): ", 1, 2)
        if confirmation != 1:
            print("삭제를 취소했습니다.")
            return
        self.quizzes.pop(number - 1)
        if self.save_state():
            print("퀴즈를 삭제하고 저장했습니다.")
        else:
            print("메모리에서 삭제했습니다. 파일 저장은 실패했습니다.")

    def show_score(self):
        if self.best_score is None:
            print("아직 완료한 퀴즈가 없습니다. 먼저 퀴즈를 풀어 보세요.")
        else:
            print(f"최고 점수: {self.best_score}점 (100점 만점)")

    def show_history(self):
        if not self.history:
            print("아직 저장된 점수 기록이 없습니다.")
            return
        print(f"\n점수 기록 (총 {len(self.history)}회, 최신순 / 날짜·시간에 시차 표시)")
        for record in reversed(self.history):
            print(f"{record['played_at']} | {record['total']}문제 중 "
                  f"{record['correct']}개 정답 | 힌트 {record['hints_used']}회 | "
                  f"{record['score']}점")

    @staticmethod
    def validate_history(history):
        if not isinstance(history, list):
            raise ValueError("history는 목록이어야 합니다.")
        for record in history:
            if not isinstance(record, dict):
                raise ValueError("점수 기록은 객체여야 합니다.")
            played_at = record["played_at"]
            if not isinstance(played_at, str) or datetime.fromisoformat(played_at).tzinfo is None:
                raise ValueError("기록 시각에는 날짜·시간과 시차가 필요합니다.")
            total, correct = record["total"], record["correct"]
            hints, score = record["hints_used"], record["score"]
            if (any(type(value) is not int for value in (total, correct, hints, score))
                    or total < 1 or not 0 <= correct <= total or not 0 <= hints <= total
                    or score != max(0, round(correct / total * 100) - hints * HINT_PENALTY)):
                raise ValueError("점수 기록의 문제 수·정답 수·힌트·점수가 올바르지 않습니다.")
        return history

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
            # 기존 파일에 history/hint가 없어도 문제와 최고점을 유지한다.
            history = self.validate_history(data.get("history", []))
        except FileNotFoundError:
            print("저장 파일이 없어 기본 퀴즈로 시작합니다.")
        except (ValueError, KeyError, TypeError, UnicodeError, OverflowError) as error:
            print(f"저장 파일이 손상되었습니다. 기본 데이터로 복구합니다. ({error})")
        except OSError as error:
            print(f"저장 파일을 읽을 수 없어 기본 데이터로 시작합니다. ({error})")
        else:
            self.quizzes = quizzes
            self.best_score = score
            self.history = history
            print(f"저장된 데이터를 불러왔습니다. 퀴즈 {len(quizzes)}개")

    def save_state(self):
        temporary_path = None
        try:
            data = {"quizzes": [quiz.to_dict() for quiz in self.quizzes],
                    "best_score": self.best_score, "history": self.history}
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

"""개별 퀴즈의 데이터와 동작."""


class Quiz:
    def __init__(self, question, choices, answer, hint=""):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 빈 문자열일 수 없습니다.")
        if (not isinstance(choices, list) or len(choices) != 4
                or any(not isinstance(c, str) or not c.strip() for c in choices)):
            raise ValueError("선택지는 내용이 있는 문자열 4개여야 합니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답 번호는 1~4의 정수여야 합니다.")
        if not isinstance(hint, str):
            raise ValueError("힌트는 문자열이어야 합니다.")
        self.question = question.strip()
        self.choices = [choice.strip() for choice in choices]
        self.answer = answer
        self.hint = hint.strip()

    def display(self):
        print(self.question)
        for number, choice in enumerate(self.choices, start=1):
            print(f"{number}. {choice}")

    def show_hint(self):
        if self.hint:
            print(f"힌트: {self.hint}")
        else:
            # 예전 저장 파일의 문제에도 힌트를 제공한다.
            wrong = [str(number) for number in range(1, 5) if number != self.answer]
            print(f"힌트: {', '.join(wrong[:2])}번은 정답이 아닙니다.")

    def check_answer(self, answer):
        return type(answer) is int and self.answer == answer

    def to_dict(self):
        return {"question": self.question, "choices": self.choices.copy(),
                "answer": self.answer, "hint": self.hint}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터는 객체여야 합니다.")
        return cls(data["question"], data["choices"], data["answer"], data.get("hint", ""))

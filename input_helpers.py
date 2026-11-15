"""메뉴와 퀴즈에서 공통으로 사용하는 입력 함수."""


def read_number(prompt, minimum, maximum):
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
        except ValueError:
            print("빈 입력이나 문자 대신 숫자를 입력하세요.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"{minimum}~{maximum} 사이의 숫자를 입력하세요.")


def read_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("빈 내용은 사용할 수 없습니다. 다시 입력하세요.")

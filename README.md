# Python 패션디자인 퀴즈 게임

대전코디세이 2차 미션으로 만드는 터미널 기반 퀴즈 게임입니다.
Python 표준 라이브러리만 사용하며, `Quiz`는 한 문제를, `QuizGame`은 메뉴·진행·저장을 담당합니다.

## 퀴즈 주제와 선정 이유

주제는 **패션디자인 기초 지식**입니다. 실루엣, 다트, 면 섬유, 시접, 균형처럼
의복 디자인과 제작에 쓰이는 기본 용어를 짧은 문제로 복습하도록 구성했습니다.
기본 문제는 5개이며 사용자가 문제를 추가할 수 있습니다.

## 실행 방법

Python 3.10 이상이 필요합니다. 별도 패키지 설치는 필요하지 않습니다.

### Ubuntu / WSL

기존 작업 폴더에서 실행할 때:

```bash
cd /home/don61/codyssey-workspace/python-quiz-game
python3 --version
python3 main.py
```

새 환경에서는 다음과 같이 기존 공개 저장소를 복제할 수 있습니다.

```bash
git clone https://github.com/heayounhwang/python-quiz-game.git
cd python-quiz-game
python3 main.py
```

### Windows

프로젝트 파일이 있는 폴더의 PowerShell에서 실행합니다.

```powershell
python --version
python main.py
```

VS Code에서 WSL을 검증하려면 WSL 터미널에서 `python3 main.py`를 실행하세요.
Windows Python 실행과 WSL Python 실행은 서로 다른 환경입니다.

## 기능 목록

| 메뉴 | 동작 |
|---|---|
| 1. 퀴즈 풀기 | 모든 문제를 순서대로 출제하고 정오답과 최종 점수를 표시 |
| 2. 퀴즈 추가 | 문제, 선택지 4개, 정답 번호 1~4를 입력받아 저장 |
| 3. 퀴즈 목록 | 현재 등록된 문제 제목과 개수를 표시 |
| 4. 점수 확인 | 완료한 게임의 최고 점수를 표시 |
| 5. 종료 | 현재 데이터를 저장하고 종료 |

- 점수는 `round(정답 수 / 전체 문제 수 * 100)`으로 계산합니다.
- 기본 5문제는 한 문제당 20점입니다. 최고 점수는 0~100점으로 비교합니다.
- 아직 완료한 게임이 없으면 최고 점수 대신 안내를 표시합니다. 0점으로 완료한 경우와 구분합니다.
- 퀴즈가 없으면 풀이·목록에서 안내합니다.
- 숫자 입력은 앞뒤 공백을 제거하고 문자·빈 입력·범위 밖 입력을 다시 받습니다.
- 문제와 선택지의 빈 내용은 허용하지 않습니다.
- Ctrl+C와 입력 종료(EOF)는 안내 후 가능한 범위에서 저장하고 종료합니다.
- 문제 추가 중 입력이 끊기면 미완성 문제는 등록하지 않습니다.
- 풀이 도중 중단하면 해당 회차 점수는 기록하지 않고 기존 최고 점수를 유지합니다.

## 파일 구조

```text
python-quiz-game/
├── main.py                 # 프로그램 시작점
├── input_helpers.py        # 공통 숫자·문자 입력 처리
├── quiz.py                 # Quiz 클래스
├── defaults.py             # 패션디자인 기본 문제 5개
├── game.py                 # QuizGame 클래스, 메뉴·진행·JSON 저장
├── state.json              # 실행 시 자동 생성되는 개인 데이터(Git 제외)
├── tests/
│   └── test_game.py         # 기능·예외·프로세스 통합 테스트
├── docs/
│   ├── test-results-wsl.txt # 실제 WSL 테스트 결과
│   ├── test-results-windows.txt # 실제 Windows 테스트 결과
│   ├── git-practice.txt     # 브랜치 및 clone/pull 실제 실행 증거
│   ├── acceptance.md        # 제출 전 검수표
│   └── screenshots/        # 학습자가 직접 캡처한 이미지 저장 위치
├── .gitignore
└── README.md
```

## state.json 설명

`game.py`와 같은 프로젝트 루트에 UTF-8 JSON으로 저장합니다.
다른 폴더에서 프로그램을 실행해도 저장 위치는 바뀌지 않습니다.
첫 실행에 파일이 없으면 기본 5문제를 사용하고, 추가·풀이 완료·종료 시 저장합니다.

아래는 필드 구조 예시입니다. `quizzes`에는 실제로 모든 등록 문제가 들어갑니다.

```json
{
  "quizzes": [
    {
      "question": "의복의 전체적인 외곽선이나 윤곽을 뜻하는 용어는?",
      "choices": ["실루엣", "다트", "시접", "안감"],
      "answer": 1
    }
  ],
  "best_score": null
}
```

- `quizzes`: 문제 목록. 각 문제는 비어 있지 않은 `question`, 선택지 4개, 정답 정수 1~4로 구성됩니다.
- `best_score`: 완료한 게임이 없으면 `null`, 있으면 0~100 정수입니다.
- JSON 구문·필드·자료형·UTF-8이 손상되면 안내하고 기본 문제와 미플레이 상태로 복구합니다.
- 손상 파일의 내용은 다음 정상 저장 시 기본 데이터로 교체됩니다. 자동 백업은 하지 않습니다.
- 읽기 오류는 안내하고 기본 데이터로 시작합니다.
- 쓰기 오류는 안내하며 메모리의 변경은 유지하지만 재실행 시 유지되지 않을 수 있습니다.
- 같은 폴더의 임시 파일에 기록한 뒤 교체해 저장 도중 기존 파일이 손상될 가능성을 줄입니다.
- `state.json`은 사용자별 실행 데이터이므로 Git에 포함하지 않습니다.

## 테스트와 검증

프로젝트 루트에서 실행합니다. 테스트는 임시 폴더를 사용해 개인 저장 데이터를 변경하지 않습니다.

```bash
python3 -m unittest discover -s tests -v
```

Windows에서는 `python -m unittest discover -s tests -v`를 사용합니다.
읽기·쓰기 권한 오류와 파일 교체 실패는 mock으로 재현하고,
메뉴 입력·추가·풀이·재시작·EOF는 별도 Python 프로세스로 검증합니다.
실제 SIGINT 테스트는 WSL/Linux에서 실행하며 Windows에서는 해당 1개가 건너뛰어집니다.

실제 결과: [WSL](docs/test-results-wsl.txt), [Windows](docs/test-results-windows.txt).
최종 조건과 남은 제출 작업은 [검수표](docs/acceptance.md)를 확인하세요.

## Git 작업과 제출 증거

기존 첫 커밋 `57dc40d`를 보존했습니다. 메뉴, 클래스, 기본 문제, 풀이, 추가, 목록,
점수, 파일 저장, 테스트, 문서를 기능별로 커밋합니다.
`codex/quiz-play`에서 풀이 기능을 개발하고 `main`으로 돌아와 `--no-ff`로 병합했습니다.
실제 Git 실습 기록은 [git-practice.txt](docs/git-practice.txt)에 남깁니다.

```bash
git log --oneline --graph --all
git branch -avv
git status --short --branch
```

제출 저장소: https://github.com/heayounhwang/python-quiz-game

### 학습자 직접 캡처 목록

아직 이미지가 없으면 제출 완료로 보지 않습니다. `docs/screenshots/`에 다음 파일을 넣으세요.

| 파일 | 캡처할 내용 |
|---|---|
| environment.png | VS Code WSL 터미널, `pwd`, `python3 --version`, `git --version` |
| menu.png | `python3 main.py` 실행 후 메뉴 5개 |
| add_quiz.png | 메뉴 2에서 새 문제·선택지 4개·정답 입력 및 추가 안내 |
| list.png | 메뉴 3에서 추가한 문제가 포함된 목록 |
| play.png | 메뉴 1에서 문제·정답 입력·최종 결과 |
| score.png | 메뉴 4에서 최고 점수 |
| git-log.png | `git log --oneline --graph --all`의 기능 커밋과 병합 그래프 |
| branch-merge.png | `git branch -avv` 및 `git log --merges --oneline` |
| clone-pull.png | `cat docs/git-practice.txt`의 clone·복제본 수정/push·원본 pull 결과 |

캡처 후에는 이미지 검토, `git add docs/screenshots`, 커밋, push가 필요합니다.
이미지에 비밀번호나 토큰이 보이지 않는지 확인하세요.

## 코드 이해하기

- `Quiz.__init__`: 질문·선택지·정답을 검사하고 객체 속성에 담습니다.
- `self`: 현재 객체를 뜻합니다. `self.quizzes`는 현재 게임의 퀴즈 목록입니다.
- `while`: 메뉴와 잘못된 입력의 재입력을 반복합니다.
- `for`: 등록된 퀴즈와 선택지를 하나씩 순회합니다.
- `list`: 퀴즈·선택지처럼 순서가 있는 데이터를 담습니다.
- `dict`: JSON 저장 시 `quizzes`, `best_score`처럼 이름과 값을 연결합니다.
- `try/except/finally`: 오류를 안내하고, 종료 시 저장을 시도하도록 만듭니다.

`git clone`은 저장소 전체를 새 폴더로 복제하고, `git pull`은 현재 저장소에 원격 변경을 가져옵니다.
`checkout`은 작업 브랜치를 바꾸거나 만들고, `merge`는 브랜치의 변경을 합칩니다.

## 복제 환경에서 확인한 실행 절차

별도 폴더로 clone한 저장소에서도 의존성 설치 없이 다음 명령으로 검증합니다.

```bash
python3 -m unittest discover -s tests -v
```

복제본에서 이 실행 안내를 추가해 commit·push한 뒤 원래 작업 폴더에서
`git pull --ff-only origin main`으로 가져오는 실습을 수행했습니다.
실제 명령과 결과는 `docs/git-practice.txt`에서 확인할 수 있습니다.

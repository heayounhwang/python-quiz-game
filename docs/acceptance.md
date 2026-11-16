# 2차 Python 퀴즈 게임 최종 검수

검수일: 2026-11-15 (Asia/Seoul). 평가자의 최종 판정을 대신하지 않으며 실제 실행 결과만 기록합니다.

**코드·자동 검증·Git 실습과 학습자가 직접 캡처한 제출 이미지 정리를 완료했습니다.**

| 필수 조건 | 결과 | 확인 근거 |
|---|---|---|
| 기존 코드·첫 커밋 보존 | PASS | 57dc40d가 main의 조상으로 유지됨 |
| Python 3.10 이상·외부 의존성 없음 | PASS | WSL 3.14.4 / Windows 3.14.3, 표준 라이브러리만 사용 |
| 메뉴 출력·선택·반복·종료 | PASS | 실제 CLI 통합 테스트 및 smoke-wsl.txt |
| Quiz / QuizGame 최소 두 클래스 | PASS | quiz.py / game.py |
| 기본 퀴즈 최소 5개·선택지 4개·정답 1~4 | PASS | defaults.py 및 기본 데이터·스키마 테스트 |
| 퀴즈 풀기·정오답·결과 | PASS | 실제 CLI에서 6문제 정답·100점 검증 |
| 퀴즈 추가·목록 | PASS | 추가 후 목록 및 재시작 시 문제 유지 검증 |
| 최고 점수 갱신·조회 | PASS | 100점 이후 낮은 점수에도 최고점 유지 |
| 미플레이·0점·빈 퀴즈 목록 | PASS | 각 상태를 구분하는 테스트 |
| 문자·빈 입력·범위 밖·앞뒤 공백 | PASS | 메뉴·정답 입력 및 공통 입력 함수 테스트 |
| Ctrl+C·EOFError | PASS | WSL 실제 SIGINT/EOF 프로세스 및 입력 중단 테스트 |
| 프로젝트 루트 state.json·UTF-8 | PASS | 실행 위치와 무관한 경로 검사, 실제 루트 파일 생성 |
| 추가 문제·최고점 재실행 유지 | PASS | 별도 프로세스 종료 후 재시작 테스트 |
| 파일 없음·손상 JSON·스키마·인코딩 복구 | PASS | 기본값 복구 및 정상 JSON 재저장 테스트 |
| 읽기·쓰기 오류 처리 | PASS | PermissionError mock 재현 및 교체 실패 시 원본 유지 |
| 의미 있는 커밋 최소 10개 | PASS | git log, 병합 커밋을 제외해도 10개 이상 |
| main 외 브랜치·checkout·merge | PASS | codex/quiz-play, reflog 및 --no-ff merge 기록 |
| clone·복제본 수정/commit/push·원본 pull | PASS | git-practice.txt의 실제 명령·출력과 HEAD 일치 확인 |
| 기존 GitHub 저장소 push | PASS | main과 codex/quiz-play push 성공 |
| README 필수 6개 항목 | PASS | 개요·주제 선정 이유·실행·기능·구조·state.json |
| 개발환경 스크린샷 | PASS | screenshots/environment.png: WSL Python·Git 버전 |
| 메뉴·추가·목록·풀이·점수 스크린샷 | PASS | screenshots/의 menu·add_quiz·list·play·result·score.png |
| Git 그래프·브랜치·clone/pull 스크린샷 | PASS | screenshots/의 git-log·branch-merge·clone-pull.png |

## 실제 검증 결과

- WSL Ubuntu Python **3.14.4**: 테스트 23개 전부 통과.
- 사용자 설치 Windows Python **3.14.3**: 22개 통과, POSIX SIGINT 1개 제외.
- Windows 번들 Python **3.12.14**에서도 22개 통과, 같은 SIGINT 1개 제외.
- 실제 SIGINT 처리는 WSL에서 통과했으므로 Windows 제외 항목을 실행한 것으로 계산하지 않습니다.
- 테스트는 임시 디렉터리에 데이터를 저장하며 사용자의 state.json을 변경하지 않습니다.
- 실제 원본 WSL 프로젝트에서도 메뉴 3·4·5 실행과 루트 state.json 생성을 확인했습니다.
- 읽기·쓰기 오류는 mock으로 재현했습니다. 운영체제의 실제 디스크 고장을 발생시킨 것은 아닙니다.

로그: [WSL](test-results-wsl.txt), [Windows 3.14](test-results-windows.txt),
[원본 실행](smoke-wsl.txt), [Git 실습](git-practice.txt).

## 발견한 문제와 조치

1. Windows 파이프 기본 인코딩과 테스트의 UTF-8 디코딩이 달라 통합 테스트가 실패했습니다.
   자식 Python 실행에 `-X utf8`을 명시한 뒤 Windows 3.14.3과 WSL에서 재검증했습니다.
2. 샌드박스의 Windows 임시 폴더를 사용하는 첫 실행이 지연되었습니다.
   해당 실행을 중단하고 승인된 실행에서 작업 폴더의 임시 디렉터리로 검증했습니다.
3. 저장 실패 시 추가 완료 안내가 모호할 수 있어 디스크 저장 성공과 메모리 추가를 구분했습니다.

## 평가 문서 적용 범위

첨부된 `미션-파이선.pdf`를 이번 Python 미션의 기준으로 적용했습니다.
`미션1 평가기준.pdf`는 13쪽 전체를 이미지로 확인했으며 Docker·터미널·개발환경을 다루는
1차 미션 자료입니다. 거기에 표시된 1차 평가 결과를 이번 Python 미션의 결과로 옮기지 않았습니다.
문서의 신규 저장소 생성 설명도 이미 완료한 작업을 반복하는 지시로 적용하지 않았습니다.

## 학습자 직접 실행 및 제출 이미지 확인

직접 제공한 원본 PNG 15개를 편집 없이 보존했습니다.
[이미지 목록](screenshots/README.md)에서 각 제출 증거에 접근할 수 있습니다.
추가한 무드보드 문제, 총 6개 목록, 100점 결과, 종료 후 6개·100점 유지,
문자·범위·빈 입력 안내, 공백 입력 후 조회, Ctrl+C 종료를 화면에서도 확인했습니다.

공백 캡처에서는 앞쪽 공백이 보이며, 뒤쪽 공백 처리는 자동 테스트로 검증했습니다.
환경 캡처는 WSL 터미널이며 VS Code 화면은 포함하지 않습니다.
clone·pull 이미지는 실제 실습 후 저장된 로그를 화면에 출력한 증거입니다.
최종 평가는 평가자의 확인에 따르며, 이 검수표는 확인 가능한 필수 항목의 자체 점검 결과입니다.

제출 저장소: https://github.com/heayounhwang/python-quiz-game

## 보너스 확장 검수

| 선택 과제 | 구현·자동 검증 | 확인 근거 |
|---|---|---|
| 랜덤 출제 | PASS | random.sample로 중복 없는 무작위 선택, 원본 순서 유지 테스트 |
| 풀 문제 수 선택 | PASS | 범위·문자·빈 입력·공백 검증, 선택한 개수만 출제 |
| 힌트 및 점수 차감 | PASS | hint 속성, 0 입력, 문제당 1회 10점 차감, 0점 하한 |
| 퀴즈 삭제 | PASS | 대상 선택·확인·취소·빈 목록·삭제 후 재실행 및 쓰기 오류 검증 |
| 점수 기록 히스토리 | PASS | 한국 시간·문제 수·정답 수·힌트 수·최종 점수 저장 및 재조회 |
| 이전 저장 데이터 호환 | PASS | hint/history가 없어도 문제·최고점 유지, 사용자 원본 파일 불변 확인 |
| 필수 기능 회귀 | PASS | 기존 23개와 보너스 17개, WSL 총 40개 통과 |
| Windows 호환 | PASS | Python 3.14.3에서 39개 통과·POSIX SIGINT 1개 제외 |

최신 결과: [WSL](test-results-bonus-wsl.txt), [Windows](test-results-bonus-windows.txt),
[실제 보너스 CLI 로그](bonus-demo.txt).
이 문서 앞부분의 23개 결과 및 기존 캡처는 필수 기능 구현 당시의 기록입니다.
보너스 기능의 새 스크린샷은 아직 직접 캡처하지 않았으며 자동 검증 로그로 구분합니다.
새 메뉴는 6번 삭제·7번 기록이며 5번 종료를 유지합니다.
기존 최고점 100점은 그대로 유지하고, 회차 기록은 확장 후 완료한 게임부터 쌓입니다.

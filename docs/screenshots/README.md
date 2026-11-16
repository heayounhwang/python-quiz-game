# 학습자가 직접 캡처한 실행 증거

채팅에 제공된 원본 PNG 27개(필수 15개·보너스 12개)를 편집 없이 복사했습니다. 파일 이름만 제출용으로 정리했으며 각 원본과 복사본의 SHA-256 일치를 확인했습니다.

버전 증거는 WSL 터미널 화면입니다. VS Code 화면을 캡처한 것은 아닙니다. Git 로그와 clean 상태 이미지는 이 이미지 정리 커밋 이전 시점입니다.

| 이미지 | 확인 내용 |
|---|---|
| [menu.png](menu.png) | WSL 실행 명령과 메뉴 5개 |
| [add_quiz.png](add_quiz.png) | 무드보드 문제·선택지·정답 등록 및 저장 완료 |
| [list.png](list.png) | 추가 문제를 포함한 총 6개 목록 |
| [play.png](play.png) | 퀴즈 출제와 4개 선택지 |
| [result.png](result.png) | 6문제 정답·100점·최고 점수 갱신 |
| [score.png](score.png) | 최고 점수 100점 조회 |
| [restart.png](restart.png) | 종료 후 재실행, 퀴즈 6개와 100점 유지 |
| [invalid-input.png](invalid-input.png) | 문자·범위 밖 숫자·빈 입력 재입력 안내 |
| [whitespace.png](whitespace.png) | 공백을 포함한 메뉴 입력 후 점수 조회 |
| [ctrl-c.png](ctrl-c.png) | Ctrl+C 입력 중단 안내와 정상 종료 |
| [git-log.png](git-log.png) | 기존 첫 커밋과 기능 커밋 15개·병합 그래프 |
| [environment.png](environment.png) | WSL 터미널 Python 3.14.4·Git 2.53.0 |
| [branch-merge.png](branch-merge.png) | main 외 브랜치와 병합 커밋 3bfcf5c |
| [clone-pull.png](clone-pull.png) | 실제 기록 파일의 clone·pull 명령 및 변경 반영 확인 |
| [git-status.png](git-status.png) | 캡처 당시 main 동기화·clean 상태 |

clone·pull 캡처는 이미 실행한 실습 로그를 출력한 화면이며, 전체 원본 로그는 [git-practice.txt](../git-practice.txt)에 있습니다.

## 보너스 5개 직접 실행 증거

원본 파일은 편집하지 않고 이름만 정리했습니다.

| 이미지 | 확인 내용 |
|---|---|
| [bonus-menu.png](bonus-menu.png) | 기존 6개 문제 로드와 확장 메뉴 7개 |
| [bonus-count.png](bonus-count.png) | 풀 문제 수 1~6 선택 입력 |
| [bonus-random.png](bonus-random.png) | 2문제 선택과 랜덤 출제, 첫 문제 시접 |
| [bonus-hint.png](bonus-hint.png) | 0번 힌트 출력과 10점 감점 안내 |
| [bonus-result.png](bonus-result.png) | 2문제 정답, 100점에서 힌트 10점 차감한 90점 |
| [bonus-history.png](bonus-history.png) | 날짜·시간·문제 수·정답 수·힌트 수·90점 기록 |
| [bonus-add-hint.png](bonus-add-hint.png) | 삭제 연습용 문제와 사용자 힌트 등록·저장 |
| [bonus-delete-confirm.png](bonus-delete-confirm.png) | 7번 연습용 문제 선택과 삭제 확인 |
| [bonus-delete.png](bonus-delete.png) | 확인 후 삭제·저장 완료 |
| [bonus-list-after-delete.png](bonus-list-after-delete.png) | 삭제 후 연습용 문제 없이 기존 6개 목록 유지 |
| [bonus-restart.png](bonus-restart.png) | 종료·재실행 후 퀴즈 6개 로드 |
| [bonus-history-restart.png](bonus-history-restart.png) | 재실행 후 2문제·힌트 1회·90점 기록 유지 |

랜덤 출제 캡처는 실제 한 회차의 선택·순서이며, 무작위 알고리즘과 원본 순서 유지는 코드 및 자동 테스트로 함께 검증합니다.

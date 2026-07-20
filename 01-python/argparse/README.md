# argparse

`argparse`는 명령줄에서 전달받은 인자를 정의하고 파싱하는 Python 표준 라이브러리다. 별도 패키지 설치 없이 간단한 CLI 프로그램이나 배치 스크립트에 사용할 수 있다.

## 핵심 개념

- `ArgumentParser`: 프로그램 설명과 명령줄 인자 규칙을 관리한다.
- `add_argument()`: 받을 인자의 이름, 타입, 기본값, 선택지 등을 정의한다.
- `parse_args()`: 실행할 때 전달된 인자를 파싱하고 결과를 네임스페이스 객체로 반환한다.
- 옵션 인자: `--port`, `--host`처럼 이름을 지정해 전달한다. 짧은 이름과 긴 이름을 함께 정의할 수도 있다.
- `type`: 입력값을 지정한 타입으로 변환하며, 변환할 수 없으면 오류를 출력한다.
- `default`: 인자를 생략했을 때 사용할 기본값을 지정한다.
- `action="store_true"`: 옵션이 있으면 `True`, 없으면 `False`가 된다.
- `choices`: 입력 가능한 값을 제한한다.
- `nargs="+"`: 하나 이상의 값을 목록으로 받는다.
- `description`, `help`: `--help`에 표시할 프로그램 및 인자 설명을 설정한다.

## 예제에서 사용하는 인자

| 인자 | 설명 | 기본값 |
| --- | --- | --- |
| `-p`, `--port` | 정수 형식의 포트 번호 | `8080` |
| `-H`, `--host` | 호스트 주소 | `127.0.0.1` |
| `--env` | `dev`, `prod`, `test` 중 실행 환경 선택 | `dev` |
| `--reload` | 전달하면 자동 재시작 여부가 `True`가 되는 플래그 | `False` |
| `--files` | 하나 이상의 파일명을 목록으로 입력 | `None` |

## 사용 방법

1. `ArgumentParser`로 파서를 만든다.
2. `add_argument()`로 프로그램이 받을 인자를 정의한다.
3. `parse_args()`로 실행 시 전달된 값을 파싱한다.
4. 파싱 결과에서 각 인자 이름으로 값에 접근해 프로그램 로직에 사용한다.

`argparse`는 타입 오류, 허용되지 않은 선택지, 필수 값 누락 등을 감지하면 사용법과 오류 메시지를 출력하고 실행을 종료한다.

## 실행 방법

저장소 루트(`/home/test0000/study-notes`)에서 실행한다.

기본값으로 실행:

```bash
python3 01-python/argparse/example.py
```

옵션을 지정해서 실행:

```bash
python3 01-python/argparse/example.py --port 3000 --host 0.0.0.0 --env prod --reload --files app.py config.py
```

짧은 옵션 사용:

```bash
python3 01-python/argparse/example.py -p 9090 -H 0.0.0.0
```

도움말 확인:

```bash
python3 01-python/argparse/example.py --help
```

## 주의할 점

- 입력값은 기본적으로 문자열이므로 숫자 등 다른 타입이 필요하면 `type`을 지정한다.
- `store_true`는 불리언 값을 직접 입력받지 않고 옵션의 존재 여부로 값을 결정한다.
- `nargs="+"`를 사용한 옵션을 전달했다면 값도 최소 한 개 입력해야 한다.
- `-h`, `--help`는 도움말 옵션으로 자동 등록되므로 다른 용도로 사용하지 않는다.

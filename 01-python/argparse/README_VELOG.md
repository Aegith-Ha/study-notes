# https://velog.io/@admusr0000/argparse-hlrbgy8d

# argparse란?

> 파이썬 스크립트를 실행할 때 전달하는 인자(argument)를 쉽게 처리하게 해주는 표준 라이브러리

예를 들어 아래처럼 스크립트를 실행할 수 있다.

```bash
python app.py --host 0.0.0.0 --port 7979
````

FastAPI 실행 시 자주 보는 `--host`, `--port` 같은 인자를 파이썬 코드 안에서 쉽게 받아서 사용할 수 있게 해준다.

---

## 사용 예제

```python
import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A simple argparse example."
    )

    parser.add_argument("-p", "--port", type=int, default=8080, help="Port number")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--reload", action="store_true", help="Enable auto reload")
    parser.add_argument("--env", choices=["dev", "prod", "test"], default="dev", help="Execution environment")
    parser.add_argument("--files", nargs="+", help="Input file list")

    return parser

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(f"port: {args.port}")
    print(f"host: {args.host}")
    print(f"env: {args.env}")
    print(f"reload: {args.reload}")
    print(f"files: {args.files}")

if __name__ == "__main__":
    main()
```

`parse_args()`를 호출하면 실행 시 전달한 인자들이 파싱되고,
`args.port`, `args.host` 같은 형태로 접근할 수 있다.

---

## 1) 옵션 인자 (optional argument)

`--port`, `--host`처럼 이름을 붙여서 전달하는 인자를 옵션 인자라고 한다.

예를 들어 아래처럼 실행할 수 있다.

```bash
python example.py --host 0.0.0.0 --port 8080
```

---

## 2) 타입 지정 (`type=`)

기본적으로 입력값은 문자열로 들어온다.
숫자를 받고 싶다면 `type=int`처럼 타입을 지정해주는 것이 좋다.

```python
parser.add_argument("-p", "--port", type=int, default=8080)
```

타입이 맞지 않으면 `argparse`가 자동으로 에러를 출력한다.

---

## 3) 기본값 (`default=`)

값을 넣지 않았을 때 사용할 기본값을 지정할 수 있다.

```python
parser.add_argument("-p", "--port", type=int, default=8080)
```

예를 들어 `--port`를 생략하면 기본값인 `8080`이 사용된다.

---

## 4) 도움말 (`description=`, `help=`)

* `description` : `-h` 실행 시 상단에 출력되는 전체 설명
* `help` : 각 argument 옆에 출력되는 개별 설명

```bash
python example.py -h
```

출력 예시는 아래와 같다.

```bash
usage: example.py [-h] [-p PORT] [-H HOST] [--reload] [--env {dev,prod,test}] [--files FILES [FILES ...]]

A simple argparse example.

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port number
  -H HOST, --host HOST  Host address
  --reload              Enable auto reload
  --env {dev,prod,test} Execution environment
  --files FILES [FILES ...]
                        Input file list
```

---

## 5) 짧은 옵션 + 긴 옵션 같이 쓰기

하나의 인자에 짧은 옵션과 긴 옵션을 같이 지정할 수 있다.

```python
parser.add_argument("-p", "--port", type=int, default=8080)
```

이렇게 하면 아래 둘 다 가능하다.

```bash
python example.py -p 9090
python example.py --port 9090
```

단, 이미 기본으로 사용 중인 `-h`는 직접 사용할 수 없다.

---

## 6) boolean 옵션 (`action="store_true"`)

`store_true`를 사용하면 옵션이 있을 때는 `True`, 없을 때는 `False`가 된다.

```python
parser.add_argument("--reload", action="store_true")
```

예를 들어:

```bash
python example.py --reload
```

위처럼 실행하면 `reload` 값은 `True`가 된다.

반대로 `--reload`를 입력하지 않으면 `False`가 된다.

---

## 7) 선택지 제한 (`choices=`)

허용할 값을 미리 제한할 수 있다.

```python
parser.add_argument("--env", choices=["dev", "prod", "test"], default="dev")
```

예를 들어 아래는 정상 실행된다.

```bash
python example.py --host 0.0.0.0 --env prod
```

출력:

```bash
port: 8080
host: 0.0.0.0
env: prod
reload: False
files: None
```

하지만 `dev`, `prod`, `test` 외의 값을 넣으면 에러가 발생한다.

---

## 8) 여러 개 값 받기 (`nargs=`)

`nargs="+"`를 사용하면 값을 1개 이상 받을 수 있다.

```python
parser.add_argument("--files", nargs="+")
```

예를 들어 아래처럼 여러 파일명을 한 번에 전달할 수 있다.

```bash
python example.py --host 0.0.0.0 --files a.txt b.txt
```

출력:

```bash
port: 8080
host: 0.0.0.0
env: dev
reload: False
files: ['a.txt', 'b.txt']
```

---

## 정리

`argparse`를 사용하면 파이썬 스크립트를 실행할 때 전달하는 인자를 쉽게 처리할 수 있다.

특히 아래 기능들을 자주 사용하게 된다.

* 옵션 인자
* 타입 지정
* 기본값 설정
* 도움말 출력
* boolean 옵션
* 선택지 제한
* 여러 값 받기

배치 스크립트나 간단한 CLI 프로그램을 만들 때 꽤 유용하다.

---

## 주의할 점

* `store_true`는 `True`, `False` 값을 직접 받는 방식이 아니라, **옵션이 있으면 `True`, 없으면 `False`** 로 동작한다.
* `nargs="+"`는 **최소 1개 이상의 값이 필요**하다.


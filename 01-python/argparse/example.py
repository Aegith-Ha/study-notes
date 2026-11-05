"""argparse 기본 옵션 유형 예제.

실행: python 01-python/argparse/example.py -p 9000 --reload --env prod --files a.txt b.txt
"""

import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A simple argparse example."
    )

    # type=int: 문자열 입력을 int로 변환한다. 변환에 실패하면 argparse가 오류를 낸다.
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port number")
    # -h는 --help가 이미 쓰고 있으므로 짧은 옵션으로 대문자 -H를 사용한다.
    parser.add_argument("-H", "--host", default="127.0.0.1", help="Host address")
    # store_true: 값 없이 옵션만 주면 True, 생략하면 False가 되는 플래그다.
    parser.add_argument("--reload", action="store_true", help="Enable auto reload")
    # choices: 목록에 없는 값이 들어오면 오류를 낸다.
    parser.add_argument("--env", choices=["dev", "prod", "test"], default="dev", help="Execution environment")
    # nargs="+": 값을 1개 이상 받아 list로 만든다. 옵션을 생략하면 None이다.
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
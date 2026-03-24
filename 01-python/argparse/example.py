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
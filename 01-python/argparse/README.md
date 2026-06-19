# argparse 실행 예시

저장소 루트(`/home/test0000/study-notes`)에서 아래 명령어로 실행한다.

```bash
python3 01-python/argparse/example.py
```

기본 실행 결과:

```text
port: 8080
host: 127.0.0.1
env: dev
reload: False
files: None
```

옵션을 지정해서 실행:

```bash
python3 01-python/argparse/example.py --port 3000 --host 0.0.0.0 --env prod --reload --files app.py config.py
```

실행 결과:

```text
port: 3000
host: 0.0.0.0
env: prod
reload: True
files: ['app.py', 'config.py']
```

도움말 확인:

```bash
python3 01-python/argparse/example.py --help
```

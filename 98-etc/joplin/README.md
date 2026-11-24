# Joplin 단방향 동기화

이 저장소의 `.md` 파일을 Joplin 데스크톱 앱의 `100. study-notes` 노트북에 폴더 구조 그대로 넣고, 실행할 때마다 바뀐 노트만 갱신한다.

```
VS Code의 md 파일 ──(sync_to_joplin.py, Data API)──▶ Joplin 데스크톱 앱 ──(기존 OneDrive 동기화)──▶ 다른 기기
```

Joplin의 동기화 설정은 건드리지 않는다. 스크립트로 바뀐 노트는 사용자가 직접 고친 노트처럼 평소대로 OneDrive에 올라간다.

## 동작 방식

| 항목 | 동작 |
|---|---|
| 대상 노트북 | Joplin 최상위의 `100. study-notes` 노트북 (없으면 생성) |
| 폴더 | 폴더마다 하위 노트북을 만든다 (`02-evals/03-golden-set` → `02-evals` › `03-golden-set`) |
| 노트 제목 | 파일 이름에서 `.md` 를 뺀 것. `README.md` 는 폴더 이름을 쓴다 (저장소 루트의 README는 `study-notes`) |
| 같은 노트 판별 | 노트의 `source_url` 필드에 `study-notes:<상대경로>` 를 저장해 두고 이 값으로 찾는다 |
| 링크 변환 | 상대경로 링크를 Joplin에 넣을 때만 바꾼다 (로컬 파일은 그대로). 아래 표 참고 |
| 갱신 | 제목, 본문(링크 변환 후), 위치 중 하나라도 바뀐 노트만 덮어쓴다. 바뀐 게 없으면 건너뛴다 |
| 제외 | 숨김 폴더(`.git`, `.codex` 등), `generated/`, `__pycache__/`, `AGENTS.md`, `CLAUDE.md` |
| 로컬에서 지운 파일 | 기본은 `[로컬에 없음]` 으로 알려만 준다. `--prune` 을 주면 Joplin에서도 삭제한다 (Joplin 휴지통으로 이동) |

### 링크 변환 규칙

| 원래 링크 | Joplin에 들어가는 링크 |
|---|---|
| 동기화되는 `.md` 파일 (`./argparse/README.md`) | 해당 노트 링크 `:/노트ID` |
| README가 있는 폴더 (`./03-golden-set/`) | 그 폴더 README 노트의 `:/노트ID` |
| README가 없는 폴더 (`./01-hybrid-search/`) | 링크를 빼고 텍스트만 남긴다. 그 폴더에 README.md를 만들면 다음 실행부터 노트 링크로 연결된다 |
| `.py` 등 다른 파일 | GitHub 주소 (`https://github.com/<owner>/<repo>/blob/main/<경로>`) |
| `http(s)://`, `#앵커`, 이미지, 코드 블록 안의 링크 | 그대로 둔다 |

- GitHub 주소는 `git remote get-url origin` 에서 자동으로 만든다. 원격이 없으면 그 링크는 그대로 둔다.
- GitHub 링크는 push된 파일만 열린다. 아직 push하지 않은 파일은 404가 난다.
- 노트를 새로 만들 때는 모든 노트의 ID를 먼저 확보한 뒤 링크를 바꿔서 한 번 더 저장한다. 그래서 처음 실행할 때도 링크가 모두 연결된다.

## 주의할 점

- **단방향이다.** Joplin에서 고친 내용은 다음 실행 때 로컬 내용으로 덮어쓰인다. 이 노트북은 읽기 전용으로 쓴다.
- **스크립트를 실행할 때 Joplin 데스크톱 앱이 켜져 있어야 한다.** Data API 서버가 앱 안에서 돌아간다.
- **상대경로 이미지는 업로드하지 않는다.** 발견하면 `[경고]` 만 출력한다.
- **노트북 이름으로 위치를 찾는다.** Joplin에서 하위 노트북 이름을 바꾸면 다음 실행 때 원래 이름의 노트북이 새로 생기고, 노트가 그쪽으로 옮겨진다.
- **WSL에서 실행하는 경우:** `.wslconfig` 에 `networkingMode=mirrored` 가 있어야 `127.0.0.1:41184` 로 Windows의 Joplin에 접속할 수 있다.

## 실행 환경 준비

1. Joplin에서 **도구 → 옵션 → Web Clipper** 로 가서 **Enable Web Clipper Service** 를 켠다.
2. 같은 화면의 **Advanced options** 에서 Authorization token을 복사한다.
3. 저장소 루트(`study-notes/.env`)에 토큰을 넣는다. `.env` 는 `.gitignore` 에 들어 있어서 커밋되지 않는다.

```
JOPLIN_TOKEN=복사한_토큰
```

4. conda 환경을 켠다. `requests` 와 `python-dotenv` 는 `environment.yml` 에 이미 들어 있다.

```bash
conda activate study-py312
```

## 실행 방법

Joplin API에 접속되는지 확인한다. `JoplinClipperServer` 가 출력되면 정상이다.

```bash
curl http://127.0.0.1:41184/ping
```

실제로 반영하지 않고 무엇이 바뀔지만 본다.

```bash
python 98-etc/joplin/sync_to_joplin.py --dry-run
```

실제로 동기화한다.

```bash
python 98-etc/joplin/sync_to_joplin.py
```

로컬에서 지운 파일에 해당하는 노트도 Joplin에서 지운다.

```bash
python 98-etc/joplin/sync_to_joplin.py --prune
```

Windows에서 더블클릭으로 실행하려면 `joplin-sync.bat` 을 Windows 폴더(예: 바탕화면)에 복사해 두고 실행한다. 저장소 안(`\\wsl$\...`)에서 바로 실행하면 UNC 경로 경고가 뜬다. 옵션은 cmd에서 `joplin-sync.bat --dry-run` 처럼 넘길 수 있다.

```bash
cp 98-etc/joplin/joplin-sync.bat /mnt/c/Users/<Windows사용자>/Desktop/
```

옵션:

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--root` | 저장소 루트 | 동기화할 로컬 폴더 |
| `--notebook` | `100. study-notes` | Joplin 최상위 노트북 이름 |
| `--base-url` | `http://127.0.0.1:41184` | Joplin Data API 주소 |
| `--dry-run` | 꺼짐 | 실제 반영 없이 변경 예정 내용만 출력 |
| `--prune` | 꺼짐 | 로컬에 없는 노트를 Joplin에서 삭제 |
| `--no-link-convert` | 꺼짐 | 링크를 변환하지 않고 본문을 그대로 넣음 |
| `--no-github` | 꺼짐 | 노트가 아닌 파일/폴더 링크를 GitHub 주소로 바꾸지 않고 그대로 둠 |
| `--github-branch` | `main` | GitHub 링크에 쓸 브랜치 |

출력 예시 (처음 실행할 때):

```
[노트북 생성] 100. study-notes
[생성] README.md
[노트북 생성] 01-python
[생성] 01-python/README.md
...

생성 22 / 갱신 0 / 변경 없음 0 / 삭제 0
```

"""로컬 .md 파일을 Joplin 의 특정 노트북으로 단방향 동기화한다.

- 폴더 구조는 하위 노트북으로 그대로 만든다.
- 노트의 source_url 에 파일 상대경로를 저장해서 같은 노트를 찾는다(중복 생성 방지).
- 상대경로 링크는 Joplin 노트 링크(:/id) 또는 GitHub 주소로 바꿔서 넣는다(로컬 파일은 그대로).
- 본문/제목/위치가 바뀐 노트만 갱신한다.
- Joplin 쪽 수정 내용은 다음 실행 때 로컬 내용으로 덮어쓴다.
"""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PREFIX = "study-notes:"
EXCLUDE_DIRS = {"generated", "__pycache__", "node_modules", "env", "venv"}
EXCLUDE_FILES = {"AGENTS.md", "CLAUDE.md"}
RELATIVE_IMAGE = re.compile(r"!\[[^\]]*\]\((?!https?://|:/)([^)\s]+)")
MD_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass
class LocalNote:
    rel_path: str  # 예: 03-rag/01-basics/README.md
    folder_parts: tuple[str, ...]  # 예: ("03-rag", "01-basics")
    title: str
    body: str

    @property
    def source_url(self) -> str:
        return SOURCE_PREFIX + self.rel_path


class JoplinClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()

    def _request(self, method: str, path: str, **kwargs):
        params = kwargs.pop("params", {}) | {"token": self.token}
        resp = self.session.request(
            method, f"{self.base_url}{path}", params=params, timeout=30, **kwargs
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"{method} {path} 실패 ({resp.status_code}): {resp.text}")
        return resp.json() if resp.text else None

    def get_all(self, path: str, fields: str) -> list[dict]:
        items: list[dict] = []
        page = 1
        while True:
            data = self._request(
                "GET", path, params={"fields": fields, "page": page, "limit": 100}
            )
            items.extend(data["items"])
            if not data.get("has_more"):
                return items
            page += 1

    def create_folder(self, title: str, parent_id: str) -> dict:
        return self._request("POST", "/folders", json={"title": title, "parent_id": parent_id})

    def create_note(self, payload: dict) -> dict:
        return self._request("POST", "/notes", json=payload)

    def update_note(self, note_id: str, payload: dict) -> None:
        self._request("PUT", f"/notes/{note_id}", json=payload)

    def delete_note(self, note_id: str) -> None:
        self._request("DELETE", f"/notes/{note_id}")


def collect_local_notes(root: Path) -> list[LocalNote]:
    notes: list[LocalNote] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if not d.startswith(".") and d not in EXCLUDE_DIRS
        )
        for name in sorted(filenames):
            if not name.endswith(".md") or name in EXCLUDE_FILES:
                continue
            path = Path(dirpath) / name
            rel = path.relative_to(root)
            folder_parts = rel.parent.parts
            stem = path.stem
            if stem.lower() == "readme":
                title = folder_parts[-1] if folder_parts else root.name
            else:
                title = stem
            body = path.read_text(encoding="utf-8")
            notes.append(LocalNote(rel.as_posix(), folder_parts, title, body))
    return notes


def build_folder_index(folders: list[dict], root_id: str) -> dict[tuple[str, ...], str]:
    """root_id 아래 노트북들을 (경로 튜플 -> folder id) 로 만든다."""
    children: dict[str, list[dict]] = {}
    for f in folders:
        children.setdefault(f["parent_id"], []).append(f)

    index: dict[tuple[str, ...], str] = {(): root_id}
    stack = [((), root_id)]
    while stack:
        parts, fid = stack.pop()
        for child in children.get(fid, []):
            key = parts + (child["title"],)
            index.setdefault(key, child["id"])
            stack.append((key, child["id"]))
    return index


def find_or_create_root(client: JoplinClient, folders: list[dict], name: str, dry_run: bool) -> str | None:
    for f in folders:
        if f["parent_id"] == "" and f["title"] == name:
            return f["id"]
    print(f"[노트북 생성] {name}")
    if dry_run:
        return None
    return client.create_folder(name, "")["id"]


def ensure_folder(
    client: JoplinClient,
    index: dict[tuple[str, ...], str],
    parts: tuple[str, ...],
    dry_run: bool,
) -> str | None:
    if parts in index:
        return index[parts]
    parent_id = ensure_folder(client, index, parts[:-1], dry_run)
    print(f"[노트북 생성] {'/'.join(parts)}")
    if dry_run:
        index[parts] = None  # type: ignore[assignment]
        return None
    fid = client.create_folder(parts[-1], parent_id)["id"]
    index[parts] = fid
    return fid


def detect_github_base(root: Path) -> str | None:
    """git remote origin 에서 https://github.com/<owner>/<repo> 형태의 주소를 만든다."""
    try:
        url = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    m = re.match(r"(?:https://|git@)github\.com[/:]([^/]+)/(.+?)(?:\.git)?/?$", url)
    return f"https://github.com/{m.group(1)}/{m.group(2)}" if m else None


class LinkConverter:
    """로컬 상대경로 링크를 Joplin 노트 링크(:/id) 또는 GitHub 링크로 바꾼다.

    - 동기화되는 .md 파일 -> :/노트ID
    - README 노트가 있는 폴더 -> 그 README 노트의 :/노트ID
    - README 가 없는 폴더 -> 링크를 빼고 텍스트만 남김
    - 그 밖의 파일 -> GitHub blob 주소 (주소를 모르면 그대로 둠)
    - http(s), mailto, #앵커, 이미지, 코드 블록 안의 링크는 그대로 둔다.
    """

    SKIP_SCHEMES = ("http://", "https://", "mailto:", "#", ":/")
    UNLINK = "\0unlink"

    def __init__(self, root: Path, id_by_rel: dict[str, str], github_base: str | None, branch: str) -> None:
        self.root = root
        self.id_by_rel = id_by_rel
        self.github_base = github_base
        self.branch = branch
        self.readme_by_dir = {
            posixpath.dirname(rel): rel
            for rel in id_by_rel
            if posixpath.basename(rel).lower() == "readme.md"
        }

    def _resolve(self, note_rel: str, target: str) -> str | None:
        path, sep, fragment = target.partition("#")
        frag = sep + fragment
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(note_rel), unquote(path)))
        if resolved.startswith(".."):
            return None  # 저장소 밖 경로는 건드리지 않음
        if resolved == ".":
            resolved = ""

        if resolved in self.id_by_rel:
            return f":/{self.id_by_rel[resolved]}{frag}"

        is_dir = path.endswith("/") or (self.root / resolved).is_dir()
        if is_dir:
            if resolved in self.readme_by_dir:
                return f":/{self.id_by_rel[self.readme_by_dir[resolved]]}{frag}"
            return self.UNLINK  # README 없는 폴더: Joplin 에 연결할 노트가 없으니 텍스트만 남김

        if self.github_base:
            return f"{self.github_base}/blob/{self.branch}/{quote(resolved)}{frag}"
        return None

    def convert(self, note_rel: str, body: str) -> str:
        def repl(m: re.Match) -> str:
            bang, text, target, title = m.group(1), m.group(2), m.group(3), m.group(4) or ""
            if bang or target.startswith(self.SKIP_SCHEMES):
                return m.group(0)
            new = self._resolve(note_rel, target)
            if new == self.UNLINK:
                return text
            return f"[{text}]({new}{title})" if new else m.group(0)

        out: list[str] = []
        in_fence = False
        for line in body.splitlines(keepends=True):
            if FENCE.match(line):
                in_fence = not in_fence
                out.append(line)
            elif in_fence:
                out.append(line)
            else:
                out.append(MD_LINK.sub(repl, line))
        return "".join(out)


def sync(args: argparse.Namespace) -> int:
    load_dotenv(REPO_ROOT / ".env")
    token = os.environ.get("JOPLIN_TOKEN")
    if not token:
        print("JOPLIN_TOKEN 이 없습니다. 저장소 루트 .env 에 JOPLIN_TOKEN=... 을 추가하세요.", file=sys.stderr)
        return 1

    root = Path(args.root).resolve()
    client = JoplinClient(args.base_url, token)

    local_notes = collect_local_notes(root)
    folders = client.get_all("/folders", "id,title,parent_id")
    root_id = find_or_create_root(client, folders, args.notebook, args.dry_run)

    # 기존 노트북 트리와 노트 수집
    if root_id:
        index = build_folder_index(folders, root_id)
        remote_notes: dict[str, dict] = {}
        for fid in set(index.values()):
            for n in client.get_all(f"/folders/{fid}/notes", "id,title,body,parent_id,source_url"):
                if n.get("source_url", "").startswith(SOURCE_PREFIX):
                    remote_notes[n["source_url"]] = n
    else:
        index = {(): None}  # type: ignore[dict-item]
        remote_notes = {}

    created = updated = unchanged = deleted = 0

    # 1단계: 노트북을 맞추고, 없는 노트를 먼저 만들어 노트 ID 를 확보한다.
    #        (링크 변환에 모든 노트의 ID 가 필요하기 때문)
    parent_ids: dict[str, str | None] = {}
    id_by_rel: dict[str, str] = {}
    new_rels: set[str] = set()
    for note in local_notes:
        for img in RELATIVE_IMAGE.findall(note.body):
            print(f"[경고] {note.rel_path}: 상대경로 이미지는 업로드하지 않습니다 -> {img}")

        parent_id = ensure_folder(client, index, note.folder_parts, args.dry_run)
        parent_ids[note.rel_path] = parent_id
        remote = remote_notes.get(note.source_url)
        if remote is not None:
            id_by_rel[note.rel_path] = remote["id"]
            continue

        print(f"[생성] {note.rel_path}")
        created += 1
        new_rels.add(note.rel_path)
        if args.dry_run:
            id_by_rel[note.rel_path] = "(새노트ID)"
            continue
        made = client.create_note({
            "title": note.title,
            "body": note.body,
            "parent_id": parent_id,
            "source_url": note.source_url,
        })
        id_by_rel[note.rel_path] = made["id"]
        remote_notes[note.source_url] = made | {"body": note.body, "title": note.title, "parent_id": parent_id}

    # 2단계: 링크를 변환한 본문으로 비교해서 바뀐 노트만 갱신한다.
    github_base = None if args.no_github else detect_github_base(root)
    converter = LinkConverter(root, id_by_rel, github_base, args.github_branch)
    for note in local_notes:
        body = note.body if args.no_link_convert else converter.convert(note.rel_path, note.body)
        parent_id = parent_ids[note.rel_path]
        is_new = note.rel_path in new_rels
        if args.dry_run and is_new:
            continue
        remote = remote_notes[note.source_url]
        if (
            remote["title"] == note.title
            and remote["body"] == body
            and (parent_id is None or remote["parent_id"] == parent_id)
        ):
            if not is_new:
                unchanged += 1
            continue

        if not is_new:
            print(f"[갱신] {note.rel_path}")
            updated += 1
        if not args.dry_run:
            client.update_note(remote["id"], {"title": note.title, "body": body, "parent_id": parent_id})

    local_urls = {n.source_url for n in local_notes}
    for url, remote in remote_notes.items():
        if url in local_urls:
            continue
        if args.prune:
            print(f"[삭제] {url.removeprefix(SOURCE_PREFIX)}")
            if not args.dry_run:
                client.delete_note(remote["id"])
            deleted += 1
        else:
            print(f"[로컬에 없음] {url.removeprefix(SOURCE_PREFIX)} (삭제하려면 --prune)")

    mode = " (dry-run, 실제 반영 안 함)" if args.dry_run else ""
    print(f"\n생성 {created} / 갱신 {updated} / 변경 없음 {unchanged} / 삭제 {deleted}{mode}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="로컬 .md 파일을 Joplin 노트북으로 단방향 동기화")
    parser.add_argument("--root", default=str(REPO_ROOT), help="동기화할 로컬 폴더 (기본: 저장소 루트)")
    parser.add_argument("--notebook", default="100. study-notes", help="Joplin 최상위 노트북 이름")
    parser.add_argument("--base-url", default="http://127.0.0.1:41184", help="Joplin Data API 주소")
    parser.add_argument("--dry-run", action="store_true", help="실제 반영 없이 변경 예정 내용만 출력")
    parser.add_argument("--prune", action="store_true", help="로컬에 없는 노트를 Joplin 에서 삭제")
    parser.add_argument("--no-link-convert", action="store_true", help="상대경로 링크를 변환하지 않고 그대로 넣음")
    parser.add_argument("--no-github", action="store_true", help="노트가 아닌 파일/폴더 링크를 GitHub 주소로 바꾸지 않음")
    parser.add_argument("--github-branch", default="main", help="GitHub 링크에 쓸 브랜치 (기본: main)")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(sync(parse_args()))

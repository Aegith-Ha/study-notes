# 에이전트 작업 규칙 (Agent Instructions)

## File Encoding Rules

## project
- This project is for study notes and learning records.
- Notes in `02-retrieval-basics` ~ `07-ml` contain no source code. Real code lives in external projects, registered in `99-projects/`, and is linked by GitHub URL (commit-hash permalink when tied to results). Never use local relative paths to other repositories.
- Only `01-python` and `98-etc` may keep small example code in this repository.

## environment
- Refer to environment.yml for the runtime environment, and use it after running conda activate study-py312.

## for prevent remove
- Do not modify or create source files unless explicitly instructed to change the source, such as "fix it" or "create it"; provide explanations only.

## git
- Do not git push, commit, and any action

## markdown
- Every .md document must start with exactly one `# 제목` (H1) on the first line, before any other content. Use a descriptive title for the note's topic (e.g. `# 검색 평가 지표 (Retrieval Metrics)`), not the file or folder name. Use `##` or lower for all other headings, and never put another `#` heading outside code blocks.
- The Joplin note title is the file name without `.md` (`README.md` -> `README`), set by `98-etc/joplin/sync_to_joplin.py`; the H1 does not affect it. Renaming a file creates a new note in Joplin (the old one is reported as `[로컬에 없음]`).
- In every .md document, place the execution section (how to run: commands, options, output examples) at the very bottom of the document.
- Name the section `## 실행 방법`. If environment setup is needed, put `## 실행 환경` (or `## 실행 환경 준비`) directly above it, so both stay at the bottom.
- Do not put run commands in concept sections; refer to the bottom section instead (e.g. "재현 명령은 하단 실행 방법 참고").
- For notes whose code lives in an external project, use `## 관련 코드` at the very bottom instead of `## 실행 방법`: link to the project (via `99-projects/`) and say that run commands are in that project's README. Do not copy run commands into the note.
- This applies when creating new documents and when editing existing ones. Generated output files (`generated/`) are excluded.

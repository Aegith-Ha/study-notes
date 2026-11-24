# Study Notes

개인 학습 및 실습 기록 저장소입니다.

## Structure
- [`01-python/`](./01-python/) : Python 기초 및 실습
- [`02-evals/`](./02-evals/README.md) : 평가 체계 (검색·생성 평가, 골든셋, LLM judge, 회귀 테스트)
- [`03-advanced-rag/`](./03-advanced-rag/README.md) : 고급 RAG 기법 (하이브리드, 리랭커, 쿼리 변환, 청킹, 파싱)
- [`04-agents/`](./04-agents/README.md) : 에이전트 확장 (Agentic RAG, tool calling·MCP, 계획-실행-검증)
- [`05-llmops/`](./05-llmops/README.md) : 운영 (트레이싱, 비용, 보안, 피드백 루프)
- [`06-ml/`](./06-ml/README.md) : ML 심화 (파인튜닝, LoRA, 서빙)
- [`98-etc/`](./98-etc/) : 단순 설명 모음
- [`99-projects/`](./99-projects/README.md) : 실제 소스가 있는 외부 프로젝트 색인

## Learning Path

```
02-evals (평가 체계)
  → 03-advanced-rag : 평가 지표로 기법별 개선 폭 비교
  → 04-agents       : 검색·도구 호출을 모델이 결정
  → 05-llmops       : 트레이싱, 비용, 보안, 피드백 루프
  → 06-ml           : 평가 체계를 갖춘 뒤 모델 자체 개선
```

## Document Index

각 주제의 세부 목차는 폴더별 README에서 관리한다.

| Section | 내용 | 상태 |
| --- | --- | --- |
| [Evals](./02-evals/README.md) | 검색 평가, 생성 평가, 골든셋, LLM judge, 회귀 테스트 | 진행 중 |
| [Advanced RAG](./03-advanced-rag/README.md) | 하이브리드 검색, 리랭커, 쿼리 변환, 청킹, 문서 파싱, 긴 컨텍스트 비교 | 예정 |
| [Agents](./04-agents/README.md) | Agentic RAG, function calling·MCP, 계획-실행-검증 루프 | 예정 |
| [LLMOps](./05-llmops/README.md) | 트레이싱, 비용 최적화, 보안, 피드백 루프 | 예정 |
| [ML](./06-ml/README.md) | PyTorch·HF, 임베딩 파인튜닝, LoRA/QLoRA, vLLM 서빙 | 예정 |
| [Projects](./99-projects/README.md) | 외부 프로젝트 색인 | 예정 |

### Evals

| Topic | GitHub README | Velog 원문 | 프로젝트 링크 |
| --- | --- | --- | --- |
| Golden Set 생성 방법 | [README](./02-evals/03-golden-set/README.md) | - | - |
| 평가 질의 만드는 방법 A~D | [01-query-sources](./02-evals/03-golden-set/01-query-sources.md) | - | - |
| Pooling 방식 | [02-pooling](./02-evals/03-golden-set/02-pooling.md) | - | - |

### Python

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| argparse | [README](./01-python/argparse/README.md) | - | [example.py](./01-python/argparse/example.py) |
| pydantic | [README](./01-python/pydantic/README.md) | - | [example.py](./01-python/pydantic/example.py) |

### ETC

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| Claude Code 단계별 사용법 | [README](./98-etc/claude/README.md) | - | - |
| Codex 프로젝트 세팅 | [README](./98-etc/codex/README.md) | - | - |
| Joplin 단방향 동기화 | [README](./98-etc/joplin/README.md) | - | [sync_to_joplin.py](./98-etc/joplin/sync_to_joplin.py) |
| VS Code 설정 | [README](./98-etc/vscode/README.md) | - | - |

## 작성 규칙

### 이름 규칙
- 폴더와 파일 이름은 `번호-kebab-case` 형식을 사용한다. (예: `01-hybrid-search/`, `01-query-sources.md`)
- 공백, 대문자, 마침표는 이름에 사용하지 않는다. (`README.md` 제외)
- 아직 노트가 없는 폴더는 `.gitkeep`으로 추적하고, 첫 노트를 만들면 `.gitkeep`을 지운다.

### 소스 코드 위치
- `02-evals` ~ `06-ml` 노트에는 소스를 두지 않는다. 실제 코드는 외부 프로젝트에 두고 링크로 연결한다.
- 외부 프로젝트는 [`99-projects/`](./99-projects/README.md)에 등록하고, 노트는 가능하면 그 문서를 거쳐 연결한다.
- 코드 링크는 GitHub URL을 쓴다. 로컬 상대경로(`../other-project/...`)는 쓰지 않는다.
- 실험 결과와 연결된 링크는 커밋 해시 고정 링크(`blob/<commit>/...`)를 쓴다.
- private 저장소라면 핵심 코드 몇 줄은 노트에 직접 인용한다.
- `01-python`, `98-etc`의 짧은 예제 코드는 예외로 이 저장소에 둔다.

### 노트 구성 (`02-evals` ~ `06-ml`)
1. 개념: 무엇이고 왜 필요한가
2. 설계 판단: 선택지와 고른 이유
3. 실험 조건: 프로젝트 커밋 해시, 평가셋 버전(질문 수, 생성일), 모델, 주요 파라미터
4. 결과: 수치는 노트에 직접 적는다 (예: 기준선 대비 Recall@10 변화)
5. 관련 코드: 프로젝트 링크 (`## 관련 코드`, 문서 하단)

### README.md
- 폴더마다 하나씩 두고, 하위 주제 목차는 해당 폴더 README에서 관리
- GitHub용
- 주요 내용, 관련 코드(또는 실행 방법), 관련 Velog 링크

### README_VELOG.md
- Velog 게시용 원문
- 개념 설명, 코드 설명, 예시, 정리
- GitHub 상대 링크는 최소화
- 작성 후 Document Index의 `Velog 원문` 칸에 링크 추가

## Git 커밋 메시지

`타입: 설명` 형식을 사용한다. 필요하면 `타입(범위): 설명`으로 범위를 적는다.

| 타입 | 의미 | 예시 |
| --- | --- | --- |
| feat | 새로운 기능, 예제 코드 추가 | feat(python): pydantic 예제 추가 |
| fix | 버그 수정 | fix: joplin 동기화 링크 변환 오류 수정 |
| docs | 문서, 학습 노트 추가/수정 | docs(evals): pooling 노트 추가 |
| style | 코드 스타일 변경(기능 변화 없음) | style: 들여쓰기 정리 |
| refactor | 리팩토링 | refactor: 평가 지표 계산 함수 분리 |
| perf | 성능 개선 | perf: 벡터 검색 속도 개선 |
| test | 테스트 추가/수정 | test: metrics 단위 테스트 추가 |
| build | 빌드, 의존성 관련 | build: environment.yml 패키지 추가 |
| ci | CI/CD | ci: GitHub Actions 수정 |
| chore | 기타 작업 | chore: .gitignore 수정 |

## 실행 환경
- [`environment.yml`](./environment.yml)

```bash
conda env create -f environment.yml
conda activate study-py312
```

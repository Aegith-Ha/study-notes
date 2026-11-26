# Study Notes

개인 학습 및 실습 기록 저장소입니다.

## Structure
- [`01-python/`](./01-python/) : Python 기초 및 실습
- [`02-retrieval-basics/`](./02-retrieval-basics/README.md) : 검색 기초 (sparse·dense 검색, 벡터 인덱스, 기본 RAG). 모든 비교의 기준선
- [`03-evals/`](./03-evals/README.md) : 평가 체계 (검색·생성 평가, 골든셋, LLM judge, 회귀 테스트)
- [`04-advanced-rag/`](./04-advanced-rag/README.md) : 고급 RAG 기법 (하이브리드, 리랭커, 쿼리 변환, 청킹, 파싱, 그래프·계층 검색)
- [`05-agents/`](./05-agents/README.md) : 에이전트 확장 (Agentic RAG, tool calling·MCP, 계획-실행-검증)
- [`06-llmops/`](./06-llmops/README.md) : 운영 (트레이싱, 비용, 보안, 피드백 루프)
- [`07-ml/`](./07-ml/README.md) : ML 심화 (파인튜닝, LoRA, 서빙)
- [`98-etc/`](./98-etc/) : 단순 설명 모음
- [`99-projects/`](./99-projects/README.md) : 실제 소스가 있는 외부 프로젝트 색인

## Learning Path

```
02-retrieval-basics (검색 기초, 기준선)
  → 03-evals        : 평가 체계 (기준선 점수 측정)
  → 04-advanced-rag : 평가 지표로 기법별 개선 폭 비교
  → 05-agents       : 검색·도구 호출을 모델이 결정
  → 06-llmops       : 트레이싱, 비용, 보안, 피드백 루프
  → 07-ml           : 평가 체계를 갖춘 뒤 모델 자체 개선
```

## Document Index

각 주제의 세부 목차는 폴더별 README에서 관리한다.

| Section | 내용 | 상태 |
| --- | --- | --- |
| [Retrieval Basics](./02-retrieval-basics/README.md) | sparse(BM25), dense(임베딩), 벡터 인덱스, 기본 RAG | 진행 중 |
| [Evals](./03-evals/README.md) | 검색 평가, 생성 평가, 골든셋, LLM judge, 회귀 테스트 | 진행 중 |
| [Advanced RAG](./04-advanced-rag/README.md) | 하이브리드 검색, 리랭커, 쿼리 변환, 청킹, 문서 파싱, 긴 컨텍스트 비교, 그래프·계층 검색 | 진행 중 |
| [Agents](./05-agents/README.md) | Agentic RAG, function calling·MCP, 계획-실행-검증 루프 | 진행 중 |
| [LLMOps](./06-llmops/README.md) | 트레이싱, 비용 최적화, 보안, 피드백 루프 | 진행 중 |
| [ML](./07-ml/README.md) | PyTorch·HF, 임베딩 파인튜닝, LoRA/QLoRA, vLLM 서빙 | 진행 중 |
| [Projects](./99-projects/README.md) | 외부 프로젝트 색인 (lawlens) | 진행 중 |

### Retrieval Basics

| Topic | GitHub README | Velog 원문 | 프로젝트 링크 |
| --- | --- | --- | --- |
| sparse 검색 | [README](./02-retrieval-basics/01-sparse-retrieval/README.md) | - | - |
| 역색인과 TF-IDF | [01-inverted-index-tfidf](./02-retrieval-basics/01-sparse-retrieval/01-inverted-index-tfidf.md) | - | - |
| BM25와 변형 | [02-bm25](./02-retrieval-basics/01-sparse-retrieval/02-bm25.md) | - | - |
| dense 검색 | [README](./02-retrieval-basics/02-dense-retrieval/README.md) | - | - |
| 임베딩 검색 기초 | [01-embedding-basics](./02-retrieval-basics/02-dense-retrieval/01-embedding-basics.md) | - | - |
| 임베딩 모델 선택 | [02-model-selection](./02-retrieval-basics/02-dense-retrieval/02-model-selection.md) | - | - |
| 벡터 인덱스 | [README](./02-retrieval-basics/03-vector-index/README.md) | - | - |
| 근사 최근접 탐색 알고리즘 | [01-ann-algorithms](./02-retrieval-basics/03-vector-index/01-ann-algorithms.md) | - | - |
| 벡터 DB | [02-vector-db](./02-retrieval-basics/03-vector-index/02-vector-db.md) | - | - |
| 기본 RAG | [README](./02-retrieval-basics/04-naive-rag/README.md) | - | - |
| 기본 RAG 파이프라인 | [01-pipeline](./02-retrieval-basics/04-naive-rag/01-pipeline.md) | - | - |
| 기본 RAG의 실패 유형 | [02-failure-modes](./02-retrieval-basics/04-naive-rag/02-failure-modes.md) | - | - |

### Evals

| Topic | GitHub README | Velog 원문 | 프로젝트 링크 |
| --- | --- | --- | --- |
| 검색 평가 지표 (Recall@k, MRR, nDCG) | [README](./03-evals/01-retrieval-metrics/README.md) | - | - |
| 정답 기반 검색 지표 | [01-reference-based](./03-evals/01-retrieval-metrics/01-reference-based.md) | - | - |
| 정답 없는 검색 지표 | [02-reference-free](./03-evals/01-retrieval-metrics/02-reference-free.md) | - | - |
| 생성 평가 지표 (Answer Correctness, Faithfulness) | [README](./03-evals/02-generation-metrics/README.md) | - | - |
| 정답 기반 생성 지표 | [01-reference-based](./03-evals/02-generation-metrics/01-reference-based.md) | - | - |
| 정답 없는 생성 지표 | [02-reference-free](./03-evals/02-generation-metrics/02-reference-free.md) | - | - |
| 골든셋 구축 (사양, 판정 기준, 데이터 형식) | [README](./03-evals/03-golden-set/README.md) | - | - |
| 골든셋 생성 방법 목록 | [00-generation-methods](./03-evals/03-golden-set/00-generation-methods.md) | - | - |
| 평가 질의 만드는 방법 A~D | [01-query-sources](./03-evals/03-golden-set/01-query-sources.md) | - | - |
| Pooling 방식 | [02-pooling](./03-evals/03-golden-set/02-pooling.md) | - | - |
| 골든셋 판정과 검수 | [03-judging-and-review](./03-evals/03-golden-set/03-judging-and-review.md) | - | - |
| 골든셋 갱신 루프 | [04-update-loop](./03-evals/03-golden-set/04-update-loop.md) | - | - |
| LLM judge | [README](./03-evals/04-llm-judge/README.md) | - | - |
| judge 설계: 채점 기준과 프롬프트 | [01-rubric-design](./03-evals/04-llm-judge/01-rubric-design.md) | - | - |
| judge 검증: 사람 판정과의 일치도 | [02-human-agreement](./03-evals/04-llm-judge/02-human-agreement.md) | - | - |
| 회귀 테스트와 CI 연결 | [README](./03-evals/05-regression-ci/README.md) | - | - |
| 회귀 테스트 설계: 계층, 통과 기준, 노이즈 | [01-gate-design](./03-evals/05-regression-ci/01-gate-design.md) | - | - |
| 회귀 테스트 파이프라인: 실행, 기준선, 리포트 | [02-ci-pipeline](./03-evals/05-regression-ci/02-ci-pipeline.md) | - | - |

### Advanced RAG

| Topic | GitHub README | Velog 원문 | 프로젝트 링크 |
| --- | --- | --- | --- |
| 지표 개선 레버 (전체 개요) | [README](./04-advanced-rag/00-improvement-levers/README.md) | - | - |
| 레버 지도: 무엇을 바꿀 수 있나 | [01-lever-map](./04-advanced-rag/00-improvement-levers/01-lever-map.md) | - | - |
| 시도 순서와 실험 규칙 | [02-order-and-rules](./04-advanced-rag/00-improvement-levers/02-order-and-rules.md) | - | - |
| 하이브리드 검색 | [README](./04-advanced-rag/01-hybrid-search/README.md) | - | - |
| 결과 합치기 방법 (가중합, RRF) | [01-fusion-methods](./04-advanced-rag/01-hybrid-search/01-fusion-methods.md) | - | - |
| 하이브리드 조정과 분석 | [02-tuning-and-analysis](./04-advanced-rag/01-hybrid-search/02-tuning-and-analysis.md) | - | - |
| 리랭커 | [README](./04-advanced-rag/02-reranking/README.md) | - | - |
| cross-encoder 리랭커 | [01-cross-encoder](./04-advanced-rag/02-reranking/01-cross-encoder.md) | - | - |
| 1차 후보 수 정하기 | [02-candidate-depth](./04-advanced-rag/02-reranking/02-candidate-depth.md) | - | - |
| 질의 변환 | [README](./04-advanced-rag/03-query-transform/README.md) | - | - |
| 질의 재작성과 HyDE | [01-query-rewrite-hyde](./04-advanced-rag/03-query-transform/01-query-rewrite-hyde.md) | - | - |
| 메타데이터 필터 추출 | [02-metadata-filter](./04-advanced-rag/03-query-transform/02-metadata-filter.md) | - | - |
| 청킹 | [README](./04-advanced-rag/04-chunking/README.md) | - | - |
| 청킹 방법 | [01-chunking-strategies](./04-advanced-rag/04-chunking/01-chunking-strategies.md) | - | - |
| 부모-자식 청크와 contextual retrieval | [02-parent-child-contextual](./04-advanced-rag/04-chunking/02-parent-child-contextual.md) | - | - |
| 문서 파싱 | [README](./04-advanced-rag/05-document-parsing/README.md) | - | - |
| PDF와 레이아웃 파싱 | [01-pdf-layout](./04-advanced-rag/05-document-parsing/01-pdf-layout.md) | - | - |
| 표와 이미지 처리 | [02-tables-images](./04-advanced-rag/05-document-parsing/02-tables-images.md) | - | - |
| 긴 컨텍스트 vs RAG | [README](./04-advanced-rag/06-long-context-vs-rag/README.md) | - | - |
| 실험 설계 | [01-experiment-design](./04-advanced-rag/06-long-context-vs-rag/01-experiment-design.md) | - | - |
| 비용과 지연 계산 | [02-cost-latency](./04-advanced-rag/06-long-context-vs-rag/02-cost-latency.md) | - | - |
| 그래프·계층 기반 검색 | [README](./04-advanced-rag/07-graph-hierarchical/README.md) | - | - |
| 그래프 기반 검색 | [01-graph-retrieval](./04-advanced-rag/07-graph-hierarchical/01-graph-retrieval.md) | - | - |
| 계층 요약 검색 | [02-hierarchical-summary](./04-advanced-rag/07-graph-hierarchical/02-hierarchical-summary.md) | - | - |

### Agents

| Topic | GitHub README | Velog 원문 | 프로젝트 링크 |
| --- | --- | --- | --- |
| Agentic RAG | [README](./05-agents/01-agentic-rag/README.md) | - | - |
| 에이전트형 검색 | [01-agentic-retrieval](./05-agents/01-agentic-rag/01-agentic-retrieval.md) | - | - |
| 에이전트 경로 평가 | [02-trajectory-evaluation](./05-agents/01-agentic-rag/02-trajectory-evaluation.md) | - | - |
| 도구 호출과 MCP | [README](./05-agents/02-tool-calling-mcp/README.md) | - | - |
| 함수 호출 | [01-function-calling](./05-agents/02-tool-calling-mcp/01-function-calling.md) | - | - |
| MCP (Model Context Protocol) | [02-mcp](./05-agents/02-tool-calling-mcp/02-mcp.md) | - | - |
| 계획-실행-검증 루프 | [README](./05-agents/03-plan-execute-verify/README.md) | - | - |
| 루프 설계 | [01-loop-design](./05-agents/03-plan-execute-verify/01-loop-design.md) | - | - |
| 실패 복구 설계 | [02-failure-recovery](./05-agents/03-plan-execute-verify/02-failure-recovery.md) | - | - |

### LLMOps

| Topic | GitHub README | Velog 원문 | 프로젝트 링크 |
| --- | --- | --- | --- |
| 트레이싱 | [README](./06-llmops/01-tracing/README.md) | - | - |
| 트레이스 설계 | [01-trace-design](./06-llmops/01-tracing/01-trace-design.md) | - | - |
| 트레이싱 도구와 운영 모니터링 | [02-tools-and-monitoring](./06-llmops/01-tracing/02-tools-and-monitoring.md) | - | - |
| 비용 최적화 | [README](./06-llmops/02-cost-optimization/README.md) | - | - |
| 캐싱 | [01-caching](./06-llmops/02-cost-optimization/01-caching.md) | - | - |
| 모델 라우팅과 입력 줄이기 | [02-model-routing](./06-llmops/02-cost-optimization/02-model-routing.md) | - | - |
| 보안 | [README](./06-llmops/03-security/README.md) | - | - |
| 프롬프트 인젝션 | [01-prompt-injection](./06-llmops/03-security/01-prompt-injection.md) | - | - |
| 문서 권한 제어와 개인정보 | [02-access-control-pii](./06-llmops/03-security/02-access-control-pii.md) | - | - |
| 피드백 루프 | [README](./06-llmops/04-feedback-loop/README.md) | - | - |
| 피드백 수집 | [01-feedback-collection](./06-llmops/04-feedback-loop/01-feedback-collection.md) | - | - |
| 피드백 루프 운영 | [02-loop-operation](./06-llmops/04-feedback-loop/02-loop-operation.md) | - | - |

### ML

| Topic | GitHub README | Velog 원문 | 프로젝트 링크 |
| --- | --- | --- | --- |
| PyTorch와 Hugging Face 기초 | [README](./07-ml/01-pytorch-hf/README.md) | - | - |
| PyTorch 기초 | [01-pytorch-basics](./07-ml/01-pytorch-hf/01-pytorch-basics.md) | - | - |
| Hugging Face 생태계 | [02-huggingface](./07-ml/01-pytorch-hf/02-huggingface.md) | - | - |
| 임베딩·리랭커 파인튜닝 | [README](./07-ml/02-embedding-finetuning/README.md) | - | - |
| 학습 데이터 만들기 | [01-training-data](./07-ml/02-embedding-finetuning/01-training-data.md) | - | - |
| 손실과 평가 | [02-loss-and-evaluation](./07-ml/02-embedding-finetuning/02-loss-and-evaluation.md) | - | - |
| LoRA와 QLoRA | [README](./07-ml/03-lora-qlora/README.md) | - | - |
| LoRA | [01-lora](./07-ml/03-lora-qlora/01-lora.md) | - | - |
| QLoRA와 적용 판단 | [02-qlora-and-when](./07-ml/03-lora-qlora/02-qlora-and-when.md) | - | - |
| vLLM 서빙 | [README](./07-ml/04-vllm-serving/README.md) | - | - |
| vLLM 기초 | [01-vllm-basics](./07-ml/04-vllm-serving/01-vllm-basics.md) | - | - |
| 서빙 성능 측정 | [02-serving-benchmark](./07-ml/04-vllm-serving/02-serving-benchmark.md) | - | - |

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
- `02-retrieval-basics` ~ `07-ml` 노트에는 소스를 두지 않는다. 실제 코드는 외부 프로젝트에 두고 링크로 연결한다.
- 외부 프로젝트는 [`99-projects/`](./99-projects/README.md)에 등록하고, 노트는 가능하면 그 문서를 거쳐 연결한다.
- 코드 링크는 GitHub URL을 쓴다. 로컬 상대경로(`../other-project/...`)는 쓰지 않는다.
- 실험 결과와 연결된 링크는 커밋 해시 고정 링크(`blob/<commit>/...`)를 쓴다.
- private 저장소라면 핵심 코드 몇 줄은 노트에 직접 인용한다.
- `01-python`, `98-etc`의 짧은 예제 코드는 예외로 이 저장소에 둔다.

### 노트 구성 (`02-retrieval-basics` ~ `07-ml`)
1. 개념: 무엇이고 왜 필요한가
2. 설계 판단: 선택지와 고른 이유
3. 관련 코드: 프로젝트 링크 (`## 관련 코드`, 문서 하단)

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

# LawLens 프로젝트 (법령 검색 RAG)

국가법령정보 Open API로 받은 법령·판례를 조문 단위로 색인하고, 하이브리드 검색과 출처가 달린 답변을 만드는 법령 검색 RAG 프로젝트다. 이후 법률 리서치 에이전트로 확장할 예정이다. 이 저장소의 학습 노트 대부분이 이 프로젝트를 실습 대상으로 삼는다.

- 저장소: [Aegith-Ha/LawLens](https://github.com/Aegith-Ha/LawLens)
- 기준 커밋: [`6720aea`](https://github.com/Aegith-Ha/LawLens/tree/6720aea86fe7fa38b4ea72203be99541ff3568a6) (2026-11, hybrid 검색을 가중 RRF로 변경)

## 단계

| 단계 | 목표 | 상태 (기준 커밋) |
| --- | --- | --- |
| Phase 1. 데이터 수집 | Open API 수집, 원본 보관, 정규화 DB, 증분 동기화 | 법령 구현, 판례 파싱은 일부 TODO |
| Phase 2. 검색 (RAG) | 조문 단위 하이브리드 검색, 인용 답변, 평가셋 | 검색·평가셋 구현, 리랭커·답변 생성은 자리만 있음 |
| Phase 3. Agent | 반복 검색, 인용 조문 추적, 판례 교차 확인 | 자리만 있음 |

## 주요 디렉토리

| 경로 | 내용 |
| --- | --- |
| [`src/lawlens/ingest`](https://github.com/Aegith-Ha/LawLens/tree/main/src/lawlens/ingest), [`sources/lawgo`](https://github.com/Aegith-Ha/LawLens/tree/main/src/lawlens/sources/lawgo) | Open API 클라이언트, 수집, 원본 저장, 동기화 |
| [`src/lawlens/parsing`](https://github.com/Aegith-Ha/LawLens/tree/main/src/lawlens/parsing) | 법령 본문 파싱, 조문 인용 추출, 텍스트 정리 |
| [`src/lawlens/indexing`](https://github.com/Aegith-Ha/LawLens/tree/main/src/lawlens/indexing) | 조문 단위 청킹, bge-m3 dense + sparse 인코딩, Milvus 스키마·저장 |
| [`src/lawlens/retrieval`](https://github.com/Aegith-Ha/LawLens/tree/main/src/lawlens/retrieval) | 하이브리드 검색(가중 RRF), 조문 직접 조회 라우팅, 검색 서비스 |
| [`src/lawlens/generation`](https://github.com/Aegith-Ha/LawLens/tree/main/src/lawlens/generation) | 답변 생성, LLM 클라이언트 (TODO) |
| [`src/lawlens/agent`](https://github.com/Aegith-Ha/LawLens/tree/main/src/lawlens/agent) | 에이전트 루프, 도구, 안전장치 (Phase 3, 자리만) |
| [`eval/golden`](https://github.com/Aegith-Ha/LawLens/tree/main/eval/golden) | 평가 질의 생성(A·B·C), pooling, 등급 판정 |
| [`eval/scoring`](https://github.com/Aegith-Ha/LawLens/tree/main/eval/scoring) | 검색 지표 계산, 평가 실행 |
| [`eval/datasets`](https://github.com/Aegith-Ha/LawLens/tree/main/eval/datasets) | 평가셋 (질의, 판정, dev/test 분할, pool 압축본) |
| [`scripts`](https://github.com/Aegith-Ha/LawLens/tree/main/scripts) | 수집·동기화·Milvus 초기화·평가 CLI |

## 평가셋

기준 커밋의 [`eval/datasets`](https://github.com/Aegith-Ha/LawLens/tree/6720aea86fe7fa38b4ea72203be99541ff3568a6/eval/datasets) 기준 (데이터 마지막 변경 2026-11-18)

| 출처 | 파일 | 상황 수 | 질의 수 (상황당 2개) | 역할 |
| --- | --- | --- | --- | --- |
| A 해석례 | `expc_rewrite.*` | 180 | 360 | 주력 |
| C 일반인 상황 | `scenario.*` | 90 | 180 | 일반인 질의 보완 |
| B 조문→질문 | `synth.*` | 30 | 60 | 진단용 |
| 합계 | | 300 | 600 | |

- 정답 등급은 2 / 1 / 0, 1 이상을 정답으로 쓴다. 상황 단위로 dev / test(3분의 1)로 나눈다.
- 판정은 LLM(Claude, Codex)이 했고 사람이 확인한 표본은 아직 없다.
- 상세 절차는 프로젝트의 [`eval/golden/README.md`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/README.md) 참고. 학습 노트 쪽 정리는 [03-evals/03-golden-set](../03-evals/03-golden-set/README.md).

## 연결된 노트

| 노트 | 연결 코드 |
| --- | --- |
| [02-retrieval-basics/01-sparse-retrieval](../02-retrieval-basics/01-sparse-retrieval/README.md) | `indexing/encoder.py` (bge-m3 sparse), `retrieval/hybrid.py` (단일 방식 검색) |
| [02-retrieval-basics/02-dense-retrieval](../02-retrieval-basics/02-dense-retrieval/README.md) | `indexing/encoder.py`, `retrieval/hybrid.py` |
| [02-retrieval-basics/03-vector-index](../02-retrieval-basics/03-vector-index/README.md) | `indexing/milvus_schema.py`, `indexing/milvus_store.py`, `scripts/init_milvus.py` |
| [02-retrieval-basics/04-naive-rag](../02-retrieval-basics/04-naive-rag/README.md) | `retrieval/service.py` (답변 생성은 미구현) |
| [03-evals/01-retrieval-metrics](../03-evals/01-retrieval-metrics/README.md) | `eval/scoring/metrics.py`, `eval/scoring/runner.py`, `scripts/eval.py` |
| [03-evals/03-golden-set](../03-evals/03-golden-set/README.md) | `eval/golden/`, `eval/datasets/` |
| [03-evals/04-llm-judge](../03-evals/04-llm-judge/README.md) | `eval/golden/judge.py`, `eval/golden/codex.py` (정답 판정용 judge) |
| [04-advanced-rag/01-hybrid-search](../04-advanced-rag/01-hybrid-search/README.md) | `retrieval/hybrid.py` (가중 RRF k=30, dense 0.6) |
| [04-advanced-rag/03-query-transform](../04-advanced-rag/03-query-transform/README.md) | `retrieval/query.py`, `parsing/references.py` (조문 직접 조회 라우팅) |
| [04-advanced-rag/04-chunking](../04-advanced-rag/04-chunking/README.md) | `indexing/chunker.py` (조문 단위 + 계층 헤더) |
| [04-advanced-rag/05-document-parsing](../04-advanced-rag/05-document-parsing/README.md) | `parsing/statute.py`, `parsing/text.py` |

- 리랭커(`retrieval/reranker.py`), 답변 생성(`generation/`), 에이전트(`agent/`)는 파일만 있고 구현 전이다. 구현되면 해당 노트(04-advanced-rag/02-reranking, 03-evals/02-generation-metrics, 05-agents)를 연결한다.
- 특정 실험 결과와 연결하는 링크는 `main`이 아니라 그 결과를 낸 커밋 해시 링크를 쓴다.

## 관련 코드

- 설치와 실행 방법은 프로젝트 [README](https://github.com/Aegith-Ha/LawLens/blob/main/README.md), [`scripts/README.md`](https://github.com/Aegith-Ha/LawLens/blob/main/scripts/README.md), [`eval/README.md`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/README.md) 참고

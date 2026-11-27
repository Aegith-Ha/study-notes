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

## 프로젝트 선택

학습 노트 README의 "기본 선택과 이유"는 프로젝트와 상관없는 일반 출발점이다. 이 프로젝트가 실제로 고른 것과, 법령 데이터라서 달라진 사정은 여기에 모은다. 레버 실험으로 설정을 바꾸면 이 표를 고친다([04-advanced-rag/00-improvement-levers](../04-advanced-rag/00-improvement-levers/README.md)). 기준 커밋 `6720aea` 기준이다.

| 주제 | 노트의 기본 선택 | 이 프로젝트의 선택 | 이유 / 상태 |
| --- | --- | --- | --- |
| 청크 ([04-chunking](../04-advanced-rag/04-chunking/README.md)) | 섹션 단위, 골든셋 판정 단위와 맞춤 | 조문 단위 + 계층 헤더 | 법령은 조문이 자연스러운 근거 단위이고 판정도 조문 단위 |
| sparse ([01-sparse-retrieval](../02-retrieval-basics/01-sparse-retrieval/README.md)) | BM25 기준선 + 학습된 sparse 별도 비교 | bge-m3 학습된 sparse(가중치만, 확장 없음) | BM25 기준선은 아직 없음. Milvus 내장 BM25로 추가할 수 있음 |
| dense ([02-dense-retrieval](../02-retrieval-basics/02-dense-retrieval/README.md)) | 후보 3~4개를 골든셋으로 비교 | bge-m3 dense, 로컬 실행 | 한 번 실행으로 dense·sparse를 함께 얻음. 다른 모델과의 비교는 아직 없음 |
| 벡터 DB ([03-vector-index](../02-retrieval-basics/03-vector-index/README.md)) | 규모·기능·라이선스로 고름 | Milvus (pymilvus 3.0) | dense·sparse를 한 collection에서 하이브리드로 비교 |
| 인덱스 | 실험은 Flat, 서비스는 HNSW 조정 | dense HNSW(M = 16, efConstruction = 200, COSINE), sparse `SPARSE_INVERTED_INDEX` + IP | 검색 파라미터 조정 실험(ef 곡선)은 아직 없음 |
| 메타데이터 필터 | 필터 필드에 스칼라 인덱스 | 시행 시작·종료일 `STL_SORT`, 법령 ID·종류·버전 `INVERTED` | 기준 시점(as_of)의 유효한 조문만 검색 |
| 하이브리드 ([01-hybrid-search](../04-advanced-rag/01-hybrid-search/README.md)) | RRF k = 60 | 가중 RRF, k = 30, dense 가중치 0.6 | 기준 커밋에서 변경. 비교 근거는 프로젝트 기록 참고 |
| 정확 조회 ([03-query-transform](../04-advanced-rag/03-query-transform/README.md)) | 식별자가 있으면 DB 조회 결과를 앞에 | "○○법 제N조" 같은 조문 인용을 직접 조회해 앞에 붙임 | 조문 번호 질문은 검색보다 조회가 정확 |
| 문서 파싱 ([05-document-parsing](../04-advanced-rag/05-document-parsing/README.md)) | 구조화된 원문 우선 | 법령 본문은 Open API의 구조화 원문. PDF 파싱은 별표·서식에만 필요 | 별표 파싱은 아직 없음 |
| 골든셋 pool ([03-golden-set](../03-evals/03-golden-set/README.md)) | 서로 다른 계열의 검색기를 섞어 pool 구성 | 같은 모델(bge-m3)의 dense·sparse·hybrid | 노트 권장보다 다양성이 낮음. 다른 계열(BM25, 다른 임베딩 모델) 추가 필요 |
| 판정 ([04-llm-judge](../03-evals/04-llm-judge/README.md)) | LLM 1차 + 사람 검수, judge 검증 후 사용 | LLM 2개(Claude, Codex) 판정 후 병합 | 사람이 확인한 표본은 아직 없음 → judge 검증 전 |
| 프롬프트·인용 ([04-naive-rag](../02-retrieval-basics/04-naive-rag/README.md)) | 문서 ID 또는 번호 인용 + 생성 뒤 인용 검증 | 번호 방식(`[1]`, `[2]`) 초안, 정보 제공 고지 문구 | 답변 생성과 인용 검증은 구현 전 (Phase 2 TODO) |
| 리랭커 ([02-reranking](../04-advanced-rag/02-reranking/README.md)) | 다국어 cross-encoder로 시작 | 없음 | 구현 전 |

- 값은 기준 커밋을 읽어 옮긴 것이다. 코드가 바뀌면 기준 커밋과 함께 고친다.

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

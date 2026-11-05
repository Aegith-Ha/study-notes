# 02-search-ir

정보 검색(IR) 관련 학습 기록 (문서를 잘 찾는 기술)

- 목표: query에 관련된 문서를 순위대로 잘 찾고, 그 품질을 측정한다.
- 평가 기준: Precision@k, Recall@k, MRR, nDCG
- 검색 백엔드: 원리 학습은 순수 Python으로 직접 구현하고, 이후 실습은 [Milvus](../00-infra/milvus/)를 사용한다.
- 데이터: 원본 corpus와 정답지(queries, qrels)는 `00-data/`에 파일로 고정하고, Milvus에는 검색용으로 적재한다.

```
00-data (원본 + 정답지) → Milvus 적재 → 검색 → qrels로 평가
```

## 진행 상태

| 단계 | 상태 | 비고 |
| --- | --- | --- |
| 00. Data | 완료 | concept 30개, query 60개 (keyword / paraphrase 쌍) |
| 01. Sparse Retrieval | 01~03 완료, 04 예정 | 04는 Milvus Lite로 시작 |
| 02. Dense Retrieval | 예정 | 목표: paraphrase nDCG@10을 0에서 끌어올리기 |
| 03. Hybrid Retrieval | 예정 | |
| 04. Reranking | 예정 | |
| 05. Evaluation | 완료 (BM25 계열 기준) | 이후 모델이 추가되면 benchmark에 행 추가 |

### 지금까지의 결과 (BM25, nDCG@10)

| query 유형 | nDCG@10 |
| --- | ---: |
| keyword | 0.683 |
| paraphrase | 0.000 |

같은 정답을 다른 단어로 물으면 BM25는 찾지 못한다. 자세한 분석은 [05. Evaluation](./05-evaluation/README.md#지금까지의-결론-bm25-계열)에 있다.

## [00. Data](./00-data/README.md)

sparse, dense, hybrid, reranking 실험이 공통으로 사용하는 데이터

- corpus, queries, qrels 생성
- keyword query와 paraphrase query를 함께 구성하여 sparse와 dense의 차이를 비교
- Milvus collection 생성 및 적재

## [01. Sparse Retrieval](./01-sparse-retrieval/README.md)

문서와 query에 등장하는 단어를 기반으로 관련 문서를 찾는 전통적인 검색 방법

1. [Inverted Index](./01-sparse-retrieval/01-inverted-index/README.md) : term dictionary와 posting list 구조
2. [TF-IDF](./01-sparse-retrieval/02-tf-idf/README.md) : TF와 IDF를 이용한 단어 가중치와 cosine similarity
3. [BM25](./01-sparse-retrieval/03-bm25/README.md) : BM25, BM25+, BM25L, BM25F의 원리와 차이
4. [Milvus BM25](./01-sparse-retrieval/04-milvus-bm25/) : Milvus full-text search와 직접 구현한 BM25 비교

## [02. Dense Retrieval](./02-dense-retrieval/)

임베딩 모델로 만든 밀집 벡터의 유사도로 의미가 비슷한 문서를 찾는 방법

- 임베딩 모델: [`dragonkue/snowflake-arctic-embed-l-v2.0-ko`](https://huggingface.co/dragonkue/snowflake-arctic-embed-l-v2.0-ko)
  - `Snowflake/snowflake-arctic-embed-l-v2.0`(XLM-RoBERTa large)을 한국어로 파인튜닝한 모델, Apache-2.0
  - 1024차원, CLS pooling, 정규화된 벡터 → cosine similarity = 내적
  - **query는 `prompt_name="query"`로 인코딩**(`query: ` prefix 추가), 문서는 prefix 없이 인코딩한다. 두 쪽을 다르게 인코딩하는 비대칭 구조라 prefix를 빼면 성능이 떨어진다.
  - CPU 기준 메모리 약 2GB, 첫 로드 시 약 2.2GB를 `~/.cache/huggingface/hub`에 다운로드한다.
- 사전 확인: `00-data`의 concept 문장 30개 중 query와 가장 가까운 문장이 정답인 비율(top-1)은 keyword 30/30, paraphrase 22/30이다. BM25가 paraphrase에서 0이던 것과 대조된다. (corpus 500개 기준 평가는 01-embedding에서 진행)

1. [Embedding](./02-dense-retrieval/01-embedding/) : 문장 임베딩과 cosine similarity
2. [Passage Split](./02-dense-retrieval/02-passage-split/) : 고정 길이, 문장 단위, overlap 분할에 따른 검색 성능 비교
3. [Milvus Dense](./02-dense-retrieval/03-milvus-dense/) : Milvus vector 검색과 인덱스 종류(HNSW, IVF) 비교

## [03. Hybrid Retrieval](./03-hybrid-retrieval/)

sparse와 dense 검색 결과를 결합하는 방법

1. [Weighted](./03-hybrid-retrieval/01-weighted/) : 점수 정규화 후 가중합
2. [RRF](./03-hybrid-retrieval/02-rrf/) : Reciprocal Rank Fusion

## [04. Reranking](./04-reranking/)

1차 검색 결과의 상위 문서를 다시 정렬하는 방법

1. [Cross-Encoder](./04-reranking/01-cross-encoder/) : query와 문서를 함께 인코딩하여 top-k 재정렬, bi-encoder와 비교

## [05. Evaluation](./05-evaluation/README.md)

검색 모델이 만든 문서 순위를 정답 데이터와 비교하고 분석하는 방법

1. [Qrels](./05-evaluation/01-qrels/README.md) : query별 정답 문서와 관련도 데이터 관리 및 검증
2. [Metrics](./05-evaluation/02-metrics/README.md) : Precision@k, Recall@k, MRR, nDCG의 개념과 계산
3. [Benchmarks](./05-evaluation/03-benchmarks/README.md) : 같은 데이터와 조건에서 sparse, dense, hybrid, rerank 성능 비교, Markdown 보고서
4. [Error Analysis](./05-evaluation/04-error-analysis/README.md) : 오검색과 미검색 사례 분류
5. [Slice Analysis](./05-evaluation/05-slice-analysis/README.md) : keyword query, paraphrase query 등 유형별 성능 비교
6. [Significance](./05-evaluation/06-significance/README.md) : 모델 간 성능 차이의 통계적 유의성 검정

## 03-rag와의 경계

| 주제 | 02-search-ir | [03-rag](../03-rag/) |
| --- | --- | --- |
| Chunking | 검색 성능 기준의 passage 분할 | 답변 품질 기준의 chunking 전략 |
| Hybrid / Rerank | 원리 구현, nDCG 비교 | 파이프라인 적용, 답변 비교 |
| 평가 | 순위 지표 | 답변 지표 (+ 순위 지표 재사용) |

## 실행 환경

repo 루트에서 `conda activate study-py312` 후 실행한다.

- 00-data, 01-sparse-retrieval, 05-evaluation: 표준 라이브러리만 사용한다.
- 02-dense-retrieval 이후: `torch`(CPU), `sentence-transformers`가 필요하다. [`environment.yml`](../environment.yml)에 포함되어 있다.

이미 만들어진 환경에 패키지만 추가할 때:

```bash
conda activate study-py312
pip install --extra-index-url https://download.pytorch.org/whl/cpu torch sentence-transformers
```

또는 `environment.yml` 기준으로 환경을 갱신한다.

```bash
conda env update -f environment.yml
```

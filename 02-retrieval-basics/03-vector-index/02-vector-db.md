# 벡터 DB (Vector Database)

벡터 인덱스를 직접 다루는 대신 저장, 검색, 메타데이터 필터, 운영을 함께 제공하는 벡터 DB의 기본 개념을 Milvus를 예로 정리한다.

- 폴더 요약과 메인 결정은 [README](./README.md) 참고
- 인덱스 알고리즘은 [01-ann-algorithms](./01-ann-algorithms.md) 참고

## 1. 왜 벡터 DB를 쓰나

| 직접 인덱스 라이브러리 (예: FAISS) | 벡터 DB (예: Milvus) |
| --- | --- |
| 벡터와 ID만 다룸 | 벡터 + 메타데이터 + 원문을 함께 저장 |
| 필터는 직접 구현 | 메타데이터 조건 검색 지원 |
| 저장·복구·동시 접근을 직접 처리 | 영속 저장, 백업, 여러 클라이언트 지원 |
| 실험에 가볍고 빠름 | 서비스 운영에 적합 |

- 처음 실험은 Flat 검색이나 가벼운 실행 형태로 시작하고, 서비스로 갈 때 서버 형태로 옮긴다.

## 2. 기본 개념 (Milvus 기준)

| 개념 | 의미 | 예 |
| --- | --- | --- |
| collection | 테이블에 해당하는 저장 단위 | `law_articles` |
| schema | 필드 정의 | `id`, `doc_id`, `doc_title`, `section_title`, `text`, `effective_date`, `embedding` |
| 벡터 필드 | 임베딩 저장. 차원 고정 | `embedding` (1024차원) |
| 스칼라 필드 | 필터·표시용 메타데이터 | `doc_title`, `effective_date` |
| index | 벡터 필드에 거는 검색 인덱스와 척도 | HNSW + COSINE |
| partition | collection 안의 물리적 구획 | 문서 종류별 (정책 / 지침 / 매뉴얼) |
| 실행 형태 | 가벼운 로컬 실행, 단일 서버, 분산 | 실험은 가벼운 형태로 시작 |

- 척도(metric)는 인덱스를 만들 때 정한다. 임베딩 모델의 권장 척도와 맞춘다([01-embedding-basics](../02-dense-retrieval/01-embedding-basics.md) 2장).
- 최근 버전은 원문 필드로 BM25 전문 검색도 지원한다. sparse와 dense를 한 DB에서 관리할 수 있어 하이브리드 실험이 쉬워진다.

## 3. 메타데이터 필터

"2024년 이후 시행된 정책만", "특정 문서 안에서만" 같은 조건 검색이다.

| 방식 | 동작 | 문제 |
| --- | --- | --- |
| 사후 필터 | 벡터로 top-k를 찾은 뒤 조건에 맞지 않는 것을 버림 | 조건이 까다로우면 k개보다 적게 남음 |
| 사전 필터 | 조건에 맞는 벡터 안에서만 검색 | 조건이 좁으면 ANN 인덱스가 비효율적일 수 있음 |

- 벡터 DB는 보통 검색 중에 조건을 함께 적용한다. 그래도 조건이 아주 좁으면 결과 수와 지연을 확인한다.
- 필터 조건을 질문에서 자동으로 뽑는 것은 [04-advanced-rag/03-query-transform](../../04-advanced-rag/03-query-transform/README.md)에서 다룬다.
- 시행일(`effective_date`) 같은 필드를 넣어 두면 구버전 문서 반환율 점검([05-regression-ci](../../03-evals/05-regression-ci/01-gate-design.md) L1)에 바로 쓸 수 있다.

## 4. sparse 벡터 저장

Milvus는 dense 벡터뿐 아니라 sparse 벡터도 저장하고 역색인으로 검색한다. sparse 벡터를 **누가 만드느냐**에 따라 두 방식이 있다.

### 4.1 직접 만든 sparse 벡터 저장

밖에서 계산한 sparse 벡터를 그대로 넣는다. Milvus는 저장하고 검색만 한다.

```text
인코딩 모델 (밖에서 실행) ──▶ {토큰ID: 가중치, ...} ──▶ SPARSE_FLOAT_VECTOR 필드
                                                          │
                                             역색인 (SPARSE_INVERTED_INDEX)
                                                          │
질문도 같은 모델로 인코딩 ──▶ 내적(IP)으로 검색 ◀───────────┘
```

| 항목 | 내용 |
| --- | --- |
| 필드 타입 | `SPARSE_FLOAT_VECTOR`. 값은 `{토큰ID: 가중치}` dict. 차원은 모델 어휘의 토큰 ID라서 Milvus는 어떤 단어인지 모른다 |
| 인덱스 | `SPARSE_INVERTED_INDEX`. 버전에 따라 WAND, MaxScore 같은 건너뛰기 알고리즘을 고를 수 있다 |
| 점수 | 내적(`IP`). 겹치는 토큰의 가중치 곱의 합으로, [03-learned-sparse](../01-sparse-retrieval/03-learned-sparse.md) 5장의 공식과 같다 |
| 가지치기 | 작은 가중치를 버리는 설정(`drop_ratio_build`, `drop_ratio_search` 등). 속도와 정확도를 맞바꾼다 |
| 맞는 경우 | 학습된 sparse(bge-m3 sparse, SPLADE)처럼 모델이 가중치를 만드는 경우 |

### 4.2 내장 전문 검색 (BM25 함수)

원문 텍스트만 넣으면 Milvus가 BM25 sparse 벡터를 직접 만든다(Milvus 2.5부터). **BM25 검색을 DB 안에서 해 주는 것**으로 보면 된다. 학습된 sparse가 아니라 [02-bm25](../01-sparse-retrieval/02-bm25.md)의 공식 기반 sparse이고, Elasticsearch의 BM25 전문 검색과 원리가 같다. 결과를 sparse 벡터 필드에 담는다는 점만 다르다.

```text
[넣을 때]
원문 ──▶ Milvus 분석기 (토큰화) ──▶ 토큰별 등장 횟수(tf) ──▶ sparse 벡터로 저장
                                                         + 컬렉션 통계 갱신 (문서 수, 평균 길이, 토큰별 문서 수)

[검색할 때]
질문 원문 ──▶ 같은 분석기로 토큰화 ──▶ 저장된 tf + 그 시점의 컬렉션 통계로 BM25 점수 계산 ──▶ top-k
```

- 스키마에 BM25 `Function`을 정의해 텍스트 필드(입력)와 sparse 필드(출력)를 연결한다. 검색할 때는 질문 원문을 그대로 넣고 metric을 `BM25`로 둔다.
- 저장되는 것은 **완성된 점수가 아니라 tf 위주의 값**이다. idf와 평균 문서 길이는 검색할 때 최신 통계로 계산한다. 그래서 문서를 추가·삭제해도 idf가 자동으로 맞춰지고, 다시 색인할 필요가 없다.
- k1, b는 인덱스 파라미터(`bm25_k1`, `bm25_b` 등)로 조정한다. [02-bm25](../01-sparse-retrieval/02-bm25.md) 3장의 파라미터 조정이 그대로 적용된다.
- 검색할 때 모델을 실행하지 않는다. 질문 처리 비용은 토큰화뿐이다.

왜 벡터로 담나
- 여기서 저장하는 sparse 벡터는 의미를 담은 임베딩이 아니라 **문서별 `{단어: tf}`**, 즉 역색인을 만드는 원재료다. 일반 BM25 엔진도 같은 정보를 "단어 → (문서, tf)" 목록으로 저장한다. 같은 데이터를 문서 기준으로 보면 sparse 벡터, 단어 기준으로 뒤집으면 역색인이다([01-inverted-index-tfidf](../01-sparse-retrieval/01-inverted-index-tfidf.md) 2장).
- BM25 점수도 "겹치는 단어마다 질문 쪽 값(idf) × 문서 쪽 값(tf 보정)을 곱해 더하는" 내적 형태라, 학습된 sparse와 같은 검색 엔진으로 계산할 수 있다.
- Milvus는 벡터 DB라 저장·색인·필터·샤딩이 벡터 필드 중심이다. BM25를 sparse 벡터 필드로 담으면 별도 텍스트 검색 엔진 없이 기존 구조를 쓰고, 4.1의 학습된 sparse와 같은 그릇·같은 `hybrid_search` API로 dense와 함께 다룰 수 있다.

이점
- **BM25 기준선을 따로 만들 필요가 없다.** 같은 컬렉션에 텍스트 필드와 BM25 함수만 추가하면 dense, 학습된 sparse와 같은 곳에서 비교할 수 있다.
- "하이브리드에 보태는 몫" 비교(dense + BM25 대 dense + 학습된 sparse)를 바로 할 수 있다([04-advanced-rag/01-hybrid-search/02-tuning-and-analysis](../../04-advanced-rag/01-hybrid-search/02-tuning-and-analysis.md) 1장: 한쪽 검색기만 성공한 질의가 많을수록 하이브리드 효과가 큼).

확인할 것
- **한국어 분석기:** 기본 분석기는 영어 기준이다. 한국어는 형태소 분석이 되는 분석기(예: lindera ko-dic)가 필요하므로, 쓰는 Milvus 버전에서 지원하는지 먼저 확인한다. 지원하지 않거나 사용자 사전을 넣을 수 없으면 Kiwi로 따로 만든 BM25보다 낮게 나올 수 있다. 토큰화 품질이 BM25 품질을 좌우한다([01-inverted-index-tfidf](../01-sparse-retrieval/01-inverted-index-tfidf.md) 4장).
- **dense 쪽 내장 기능과는 다르다:** 최근 Milvus에는 외부 임베딩 API를 호출해 dense 벡터를 대신 만들어 주는 기능도 있다. 이것은 모델 호출을 Milvus에 맡기는 것이지, 내장 BM25처럼 공식으로 계산하는 것이 아니다. 버전별 지원 범위는 문서로 확인한다.

### 4.3 비교

| | 직접 만든 벡터 (4.1) | 내장 BM25 (4.2) |
| --- | --- | --- |
| 벡터를 만드는 곳 | 밖 (bge-m3, SPLADE 등) | Milvus 내부 |
| 가중치 | 학습된 가중치 | BM25 공식 |
| 넣는 것 | `{토큰ID: 가중치}` | 원문 텍스트 |
| 질문 처리 | 밖에서 모델로 인코딩 | 원문 그대로 |
| 점수 | 내적 (IP) | BM25 |
| 문서 추가 시 | 새 문서만 인코딩 | 통계 자동 갱신, 재색인 불필요 |
| 검색할 때 모델 실행 | 있음 | 없음 (토큰화만) |
| 토큰화 조정 | 불가 (모델 토크나이저 고정) | 분석기 설정으로 가능 (사용자 사전은 분석기가 지원할 때만) |
| 관련 노트 | [03-learned-sparse](../01-sparse-retrieval/03-learned-sparse.md) | [02-bm25](../01-sparse-retrieval/02-bm25.md) |

- 두 방식을 한 컬렉션에 함께 두면 BM25, 학습된 sparse, dense를 별도 검색 엔진 없이 한곳에서 비교할 수 있다. 문서 ID와 메타데이터가 같아 비교 조건을 맞추기 쉽다.
- 여러 필드를 한 번에 검색하고 합치는 기능(`hybrid_search` + `RRFRanker` / `WeightedRanker`)이 있다. 다만 지원하는 합치기 방식이 원하는 것과 다르면(예: 가중 RRF) 필드별로 따로 검색한 뒤 밖에서 합친다([04-advanced-rag/01-hybrid-search](../../04-advanced-rag/01-hybrid-search/README.md)).
- 필드 타입, 인덱스 이름, 파라미터는 Milvus 버전마다 다르다. 쓰는 버전의 문서를 기준으로 확인하고 버전을 결과와 함께 기록한다.

## 5. 운영에서 신경 쓸 것

| 항목 | 내용 |
| --- | --- |
| 모델 교체 | 차원이 바뀌면 collection을 새로 만든다. 새 collection을 채운 뒤 바꿔 끼운다 |
| 문서 갱신 | 개정된 섹션은 삭제 후 추가 또는 갱신. `doc_id`는 고정하고 `doc_version`으로 구분 ([03-golden-set](../../03-evals/03-golden-set/README.md) 데이터 형식) |
| 백업 | 벡터 재생성은 비싸다. 정기 백업과 복구 절차를 확인한다 |
| 메모리 | HNSW는 메모리를 많이 쓴다. 벡터 수 × 차원 × 4바이트보다 넉넉하게 잡는다 |
| 일관성 | 넣자마자 검색되지 않을 수 있다. 평가 전에 색인 완료를 확인한다 |

## 6. 확인할 점

- 평가 실행 전에 collection의 벡터 수가 문서 수와 같은지 확인한다. 색인이 일부만 된 상태로 평가하면 Recall이 낮게 나온다.
- 백업 데이터를 지우는 작업(collection 삭제 등)은 운영 데이터에 직접 하지 않는다.

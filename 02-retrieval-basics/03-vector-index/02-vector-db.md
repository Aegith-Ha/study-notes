# 벡터 DB (Vector Database)

벡터 인덱스를 직접 다루는 대신 저장, 검색, 메타데이터 필터, 운영을 함께 제공하는 벡터 DB의 기본 개념을 Milvus를 예로 정리한다.

- 폴더 요약과 기본 선택은 [README](./README.md) 참고
- 인덱스 알고리즘은 [01-ann-algorithms](./01-ann-algorithms.md) 참고

## 1. 왜 벡터 DB를 쓰나

| 직접 인덱스 라이브러리 (예: FAISS) | 벡터 DB (예: Milvus) |
| --- | --- |
| 벡터와 ID만 다룸 | 벡터 + 메타데이터 + 원문을 함께 저장 |
| 필터는 직접 구현 | 메타데이터 조건 검색 지원 |
| 저장·복구·동시 접근을 직접 처리 | 영속 저장, 백업, 여러 클라이언트 지원 |
| 실험에 가볍고 빠름 | 서비스 운영에 적합 |

- 처음 실험은 Flat 검색이나 가벼운 실행 형태로 시작하고, 서비스로 갈 때 서버 형태로 옮긴다.

### 선택지 비교

| 종류 | 예 | 강점 | 약점 | 맞는 경우 |
| --- | --- | --- | --- | --- |
| 전용 벡터 DB | Milvus | 대규모·분산, 인덱스 종류가 많음, dense·sparse·BM25·멀티 벡터를 한 collection에 | 구성 요소가 많아 운영이 무거움 (가벼운 실행 형태로 시작 가능) | 수백만 개 이상, 여러 검색 방식 비교 |
| 전용 벡터 DB | Qdrant, Weaviate | 단일 서버로 시작하기 쉬움, 필터 검색이 잘 되어 있음, sparse·하이브리드 지원 | 기능 범위와 대규모 운영 방식이 제품마다 다름 | 중소 규모 서비스 |
| 기존 DB 확장 | pgvector (PostgreSQL) | 원문·메타데이터·벡터를 한 DB에서 SQL로, 트랜잭션, 운영 경험 재사용 | 아주 큰 규모나 높은 처리량에서는 전용 DB보다 불리 | 이미 PostgreSQL을 쓰고 문서 수가 많지 않을 때 |
| 검색 엔진 | Elasticsearch, OpenSearch | BM25·형태소 분석기·사용자 사전이 성숙, 벡터 검색도 지원 | 벡터 전용 기능은 벡터 DB보다 늦게 들어옴, 메모리 사용 큼 | sparse가 중요하고 이미 검색 엔진을 쓸 때 |
| 가벼운 내장형 | Chroma, LanceDB, FAISS | 설치 없이 파일·프로세스 안에서 실행 | 동시 접근, 운영 기능이 약함 | 실험, 노트북, 소규모 |

### 라이선스와 비용

직접 설치해 쓰는 것(self-hosted)은 대부분 무료 오픈소스이고, 같은 제품의 관리형 클라우드는 유료다. 2026년 조사 기준이며, 라이선스는 바뀔 수 있으니 도입 전에 각 저장소의 LICENSE 파일을 확인한다.

| 제품 | 라이선스 (직접 설치) | 상용 서비스에 써도 되나 | 유료 선택지 |
| --- | --- | --- | --- |
| Milvus | Apache 2.0 | 됨 | Zilliz Cloud (관리형) |
| Qdrant | Apache 2.0 | 됨 | Qdrant Cloud (관리형, 무료 등급 있음) |
| Weaviate | BSD-3-Clause (핵심). 일부 새 코드는 별도 상용 라이선스 | 핵심은 됨. 상용 라이선스 부분을 쓰는지 확인 | Weaviate Cloud (관리형) |
| pgvector | PostgreSQL License (MIT·BSD와 비슷한 허용형) | 됨 | 클라우드 PostgreSQL 서비스 비용만 |
| OpenSearch | Apache 2.0 | 됨 | 클라우드 관리형 서비스 |
| Elasticsearch | AGPLv3, SSPL, Elastic License 2.0 중 선택. 일부 기능은 유료 구독 | 내부 사용은 보통 문제없음. 고쳐서 외부에 서비스로 제공하거나 "검색 서비스" 자체를 팔면 조건 확인 | Elastic Cloud, 유료 구독 |
| Chroma | Apache 2.0 | 됨 | Chroma Cloud (관리형) |
| LanceDB | Apache 2.0 | 됨 | 관리형 서비스 |
| FAISS | MIT | 됨 | 없음 (라이브러리) |
| Pinecone | 비공개 (관리형 전용) | 됨 (서비스 약관에 따름) | 사용량 기반 유료, 무료 등급 있음 |

라이선스 읽는 법
- **허용형 (Apache 2.0, MIT, BSD, PostgreSQL License):** 상용 서비스에 그대로 써도 되고 코드를 고쳐도 공개할 의무가 없다. 저작권 표시와 라이선스 문구만 유지한다. Apache 2.0은 특허 사용 허락도 포함한다.
- **AGPLv3:** 쓰는 것은 자유지만, **고친 코드를 네트워크 서비스로 제공하면 그 코드를 공개해야 한다.** 고치지 않고 그대로 쓰면 보통 문제없다.
- **SSPL, Elastic License 2.0:** 오픈소스 정의(OSI)에 맞지 않는 소스 공개형이다. 내부 사용은 되지만, 그 제품을 관리형 서비스로 다른 회사에 파는 것을 막는다.
- **관리형 클라우드:** 라이선스 대신 비용(저장량, 처리량, 노드 시간)과 데이터 위치를 본다. 데이터를 외부로 보낼 수 없으면 직접 설치형만 남는다.

- 무료로 직접 설치해도 서버, 메모리, 운영 인력 비용은 든다. 문서 수가 적으면 관리형 무료 등급이나 pgvector가 더 쌀 수 있다.
- 라이선스 판단이 애매하면(AGPL 코드를 고칠 계획 등) 회사의 법무 검토를 받는다. 이 표는 출발점일 뿐이다.

- 고를 때 볼 것: 문서 규모, 필요한 검색 방식(BM25, sparse, 멀티 벡터, 필터), 한국어 분석기 지원, 운영 인력, 이미 쓰는 인프라, 라이선스와 비용.
- 검색 품질은 DB보다 임베딩 모델·청크·토큰화가 대부분 정한다. 같은 인덱스 종류와 파라미터면 DB를 바꿔도 결과는 비슷하다. DB는 기능과 운영 편의로 고른다.

## 2. 기본 개념 (Milvus 기준)

| 개념 | 의미 | 예 |
| --- | --- | --- |
| collection | 테이블에 해당하는 저장 단위 | `doc_chunks` |
| schema | 필드 정의 | `id`, `doc_id`, `doc_title`, `section_title`, `text`, `effective_date`, `embedding` |
| 벡터 필드 | 임베딩 저장. 차원 고정 | `embedding` (1024차원) |
| 스칼라 필드 | 필터·표시용 메타데이터 | `doc_title`, `effective_date` |
| index | 벡터 필드에 거는 검색 인덱스와 척도 | HNSW + COSINE |
| partition | collection 안의 물리적 구획 | 문서 종류별 (정책 / 지침 / 매뉴얼) |
| partition key | 필드 값으로 구획을 자동으로 나눔 | `tenant_id`별로 나눠 사용자 그룹마다 따로 검색 |
| 스칼라 인덱스 | 필터에 쓰는 스칼라 필드에 거는 인덱스 | 문자열은 INVERTED, 값 종류가 적으면 BITMAP |
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
- 필터에 자주 쓰는 필드에는 스칼라 인덱스를 건다. 없으면 조건 확인이 전체 훑기가 되어 느려진다.
- 좁은 필터에서는 ANN Recall이 떨어질 수 있다. 필터 조건별로 따로 잰다([01-ann-algorithms](./01-ann-algorithms.md) 3.2).
- 자주 나누는 큰 구분은 partition key로 나누면 필터 대신 구획 검색이 된다. 사용자 그룹별 접근 제한(멀티 테넌시)에도 쓴다.
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
- 멀티 벡터(ColBERT)는 sparse와 또 다른 필드 형태(Array of Structs + MAX_SIM, 2.6.4 이상)로 저장한다. 저장 방식은 [02-dense-retrieval/02-multi-vector](../02-dense-retrieval/02-multi-vector.md) 9장 참고

## 5. 운영에서 신경 쓸 것

| 항목 | 내용 |
| --- | --- |
| 모델 교체 | 차원이 바뀌면 collection을 새로 만든다. 새 collection을 채운 뒤 바꿔 끼운다 |
| 문서 갱신 | 개정된 섹션은 삭제 후 추가 또는 갱신. `doc_id`는 고정하고 `doc_version`으로 구분 ([03-golden-set](../../03-evals/03-golden-set/README.md) 데이터 형식) |
| 백업 | 벡터 재생성은 비싸다. 정기 백업과 복구 절차를 확인한다 |
| 메모리 | HNSW는 원본 벡터 + 그래프 연결을 메모리에 둔다. 100만 × 1,024차원이면 약 4.2GB, 색인·삭제 여유까지 1.5~2배 ([01-ann-algorithms](./01-ann-algorithms.md) 2.2) |
| 일관성 | 넣자마자 검색되지 않을 수 있다. 평가 전에 색인 완료를 확인한다 (아래 5.1) |
| 삭제 | 삭제는 바로 지워지지 않고 표시만 된다. 정리(compaction) 전까지 공간을 차지하고 검색에서만 빠진다 |

### 5.1 Milvus 내부 동작 (평가에 영향을 주는 것)

```text
넣은 데이터 ──▶ growing segment (아직 인덱스 없음, 정확 검색 또는 임시 인덱스)
                    │ 일정 크기가 되거나 flush하면
                    ▼
               sealed segment ──▶ 인덱스 생성 (HNSW 등)
검색은 두 종류 segment를 모두 보고 결과를 합친다
```

| 개념 | 내용 | 평가에 주는 영향 |
| --- | --- | --- |
| 일관성 수준 | Strong (넣은 것 바로 보임) / Bounded (조금 늦게 보임, 기본값) / Session (내가 넣은 것은 보임) / Eventually (가장 느슨) | 넣은 직후 평가하면 일부 문서가 빠질 수 있음. 평가할 때는 Strong으로 검색하거나 flush 후 충분히 기다림 |
| growing / sealed segment | 새 데이터는 인덱스가 없는 segment에 먼저 들어감 | 같은 데이터라도 인덱스가 만들어지기 전과 후의 결과가 다를 수 있음 |
| compaction | 작은 segment를 합치고 삭제 표시된 데이터를 실제로 지움 | segment 구성이 바뀌면 ANN 결과 순서가 조금 달라질 수 있음 |
| load | collection을 메모리에 올려야 검색 가능 | 메모리 부족이면 load 실패. 메모리 계산 필요 |

- 평가 전 순서: 넣기 → flush → 인덱스 생성 완료 확인 → load → 벡터 수 확인 → 검색.
- ANN 결과가 실행마다 조금씩 달라지는 것은 이 구조 때문일 수 있다. 회귀 테스트에서는 이 노이즈를 감안한다([03-evals/05-regression-ci/01-gate-design](../../03-evals/05-regression-ci/01-gate-design.md) 5장).

## 6. 확인할 점

- 평가 실행 전에 collection의 벡터 수가 문서 수와 같은지 확인한다. 색인이 일부만 된 상태로 평가하면 Recall이 낮게 나온다.
- 백업 데이터를 지우는 작업(collection 삭제 등)은 운영 데이터에 직접 하지 않는다.

# 벡터 인덱스 (Vector Index)

임베딩 벡터를 빠르게 찾기 위한 인덱스와 벡터 DB를 정리한다. 인덱스는 검색 품질을 올리는 것이 아니라 **정확 검색을 얼마나 덜 놓치면서 빠르게 하느냐**의 문제다. 이 README에는 기본 선택과 이유를 두고, 알고리즘과 벡터 DB 설명은 하위 노트에 둔다.

- 임베딩 모델은 [02-dense-retrieval](../02-dense-retrieval/README.md) 참고
- 검색 품질 지표는 [03-evals/01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md) 참고

## 하위 노트

- [01-ann-algorithms](./01-ann-algorithms.md): 정확 검색과 근사 검색(Flat이 충분한 규모 계산), IVF·HNSW·PQ 원리와 파라미터, IVF 손계산, HNSW 메모리 계산, 그 밖의 인덱스(SQ8, DiskANN, GPU, AUTOINDEX), ANN Recall과 골든셋 Recall의 차이, 파라미터 조정 절차, 필터와 함께 쓸 때, 공개 벤치마크
- [02-vector-db](./02-vector-db.md): 벡터 DB를 쓰는 이유와 선택지 비교(Milvus, Qdrant, pgvector, Elasticsearch 등)와 라이선스·비용(상용 사용 가능 여부), Milvus 기본 개념(partition key, 스칼라 인덱스), 메타데이터 필터, sparse 벡터 저장(직접 만든 벡터 / 내장 BM25), 운영에서 신경 쓸 것, Milvus 내부 동작(일관성 수준, segment, compaction)

## 인덱스 품질과 검색 품질

| 단계 | 질문 | 지표 | 정답 |
| --- | --- | --- | --- |
| 모델 비교 | 어떤 임베딩 모델이 정답을 잘 가져오나 | Recall@k (골든셋) | 골든셋 |
| 인덱스 조정 | 인덱스가 정확 검색을 얼마나 따라가나 | **ANN Recall@k** | Flat 검색 결과 |
| 최종 확인 | 고른 모델 + 인덱스로 정답을 잘 가져오나 | Recall@k (골든셋) | 골든셋 |

- 모델은 Flat으로 비교하고, 고른 모델로 인덱스 파라미터를 조정한다. 두 오차를 섞지 않는다.

## 기본 선택과 이유

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 실험 단계 인덱스 | Flat | 문서 수가 많지 않으면 충분히 빠르고, 모델 비교에 근사 오차가 없음 |
| 서비스 인덱스 후보 | HNSW | 정확도·속도 균형. 메모리 부족 시 IVF 계열 |
| 인덱스 통과 기준 | ANN Recall@10 ≥ 0.95, p95 검색 지연 목표 이내 | 인덱스가 골든셋 Recall을 깎는 폭을 작게 |
| 파라미터 조정 | 색인 파라미터는 기본값, 검색 파라미터(ef, nprobe)를 올리며 기준을 만족하는 가장 작은 값 선택. 자주 쓰는 필터 조건별로도 ANN Recall 측정 | 재색인 없이 조정 가능한 것부터. 좁은 필터에서 Recall이 떨어질 수 있음 |
| 메모리 줄이기 | 필요할 때 SQ8 → PQ 순, refine 옵션 함께 | 정확도 손실이 작은 것부터 |
| 척도 | 임베딩 모델 권장 척도 (정규화 + COSINE 기본) | 모델 학습 방식과 일치 |
| 벡터 DB | 규모와 필요한 검색 방식으로 고름. 여러 검색 방식을 한곳에서 비교하려면 Milvus 같은 전용 DB, 문서 수가 적고 PostgreSQL을 이미 쓰면 pgvector | 검색 품질은 DB보다 모델·청크·토큰화가 정함. DB는 기능·운영·라이선스로 고름 ([02-vector-db](./02-vector-db.md) 1장) |
| 평가할 때 일관성 | 색인 완료를 확인한 뒤 평가. Milvus라면 넣기 → flush → 인덱스 완료 → load 후 Strong으로 검색 | 넣은 직후에는 일부 문서가 검색되지 않을 수 있음 |
| 메타데이터 | 문서 제목, 문서 종류, 섹션 제목, 시행일, `doc_id`, `doc_version` | 필터, 노후화 점검, 골든셋 연결 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): collection 스키마·인덱스 [`milvus_schema.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/milvus_schema.py), 저장 [`milvus_store.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/milvus_store.py), 생성 [`init_milvus.py`](https://github.com/Aegith-Ha/LawLens/blob/main/scripts/init_milvus.py)
  - sparse는 [02-vector-db](./02-vector-db.md) 4.1 방식이다. bge-m3 `lexical_weights`를 `SPARSE_FLOAT_VECTOR` 필드에 넣고 `SPARSE_INVERTED_INDEX` + `IP`로 검색한다. 내장 BM25(4.2)는 쓰지 않는다
  - 인덱스 파라미터 비교 스크립트는 아직 없음
- 실행 방법은 연결된 프로젝트 README 참고
- 참고: Milvus (`pymilvus`), FAISS

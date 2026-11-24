# 벡터 인덱스 (Vector Index)

임베딩 벡터를 빠르게 찾기 위한 인덱스와 벡터 DB를 정리한다. 인덱스는 검색 품질을 올리는 것이 아니라 **정확 검색을 얼마나 덜 놓치면서 빠르게 하느냐**의 문제다. 이 README에는 메인 결정과 결과를 두고, 알고리즘과 벡터 DB 설명은 하위 노트에 둔다.

- 임베딩 모델은 [02-dense-retrieval](../02-dense-retrieval/README.md) 참고
- 검색 품질 지표는 [03-evals/01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md) 참고

## 하위 노트

- [01-ann-algorithms](./01-ann-algorithms.md): 정확 검색과 근사 검색, IVF·HNSW·PQ 원리와 파라미터, IVF 손계산, ANN Recall과 골든셋 Recall의 차이
- [02-vector-db](./02-vector-db.md): 벡터 DB를 쓰는 이유, Milvus 기본 개념, 메타데이터 필터, 운영에서 신경 쓸 것

## 인덱스 품질과 검색 품질

| 단계 | 질문 | 지표 | 정답 |
| --- | --- | --- | --- |
| 모델 비교 | 어떤 임베딩 모델이 정답을 잘 가져오나 | Recall@k (골든셋) | 골든셋 |
| 인덱스 조정 | 인덱스가 정확 검색을 얼마나 따라가나 | **ANN Recall@k** | Flat 검색 결과 |
| 최종 확인 | 고른 모델 + 인덱스로 정답을 잘 가져오나 | Recall@k (골든셋) | 골든셋 |

- 모델은 Flat으로 비교하고, 고른 모델로 인덱스 파라미터를 조정한다. 두 오차를 섞지 않는다.

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 실험 단계 인덱스 | Flat | 문서 수가 많지 않으면 충분히 빠르고, 모델 비교에 근사 오차가 없음 |
| 서비스 인덱스 후보 | HNSW | 정확도·속도 균형. 메모리 부족 시 IVF 계열 |
| 인덱스 통과 기준 | ANN Recall@10 ≥ 0.95, p95 검색 지연 목표 이내 | 인덱스가 골든셋 Recall을 깎는 폭을 작게 |
| 척도 | 임베딩 모델 권장 척도 (정규화 + COSINE 기본) | 모델 학습 방식과 일치 |
| 벡터 DB | Milvus (가벼운 실행 형태로 시작) | 메타데이터 필터, BM25 전문 검색, 운영 기능 |
| 메타데이터 | 법령명, 법령 종류, 조문 제목, 시행일, `doc_id`, `doc_version` | 필터, 노후화 점검, 골든셋 연결 |

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| 벡터 DB / 버전, 실행 형태 | - |
| 임베딩 모델 / 차원 | - |
| 벡터 수 | - |
| 인덱스 종류, 파라미터 | - (예: HNSW M, efConstruction, ef) |
| 척도 | - |
| 측정 질의 | - (골든셋 dev / 운영 표본, 질의 수) |

## 결과

### 인덱스 파라미터 비교

| 인덱스 | 파라미터 | ANN Recall@10 | 골든셋 Recall@5 | p95 지연 | 메모리 |
| --- | --- | --- | --- | --- | --- |
| Flat | - | 1.000 | - | - | - |
| HNSW | M = 16, ef = 64 | - | - | - | - |
| HNSW | M = 16, ef = 128 | - | - | - | - |
| IVF-Flat | nlist = -, nprobe = - | - | - | - | - |

- Flat의 ANN Recall은 정의상 1.000이다. 골든셋 Recall@5가 Flat과 거의 같으면서 지연이 목표 이내인 가장 가벼운 설정을 고른다.

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): collection 스키마·인덱스 [`milvus_schema.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/milvus_schema.py), 저장 [`milvus_store.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/milvus_store.py), 생성 [`init_milvus.py`](https://github.com/Aegith-Ha/LawLens/blob/main/scripts/init_milvus.py)
  - 인덱스 파라미터 비교 스크립트는 아직 없음
- 실행 방법은 연결된 프로젝트 README 참고
- 참고: Milvus (`pymilvus`), FAISS

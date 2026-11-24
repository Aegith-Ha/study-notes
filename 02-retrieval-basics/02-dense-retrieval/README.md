# dense 검색 (Dense Retrieval)

질의와 문서를 임베딩 벡터로 바꿔 의미가 가까운 문서를 찾는 dense 검색을 정리한다. BM25와 함께 두 번째 검색 기준선이다. 이 README에는 메인 결정과 기준선 결과를 두고, 원리와 모델 선택 방법은 하위 노트에 둔다.

- 평가 지표는 [03-evals/01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md) 참고
- sparse 검색은 [01-sparse-retrieval](../01-sparse-retrieval/README.md), 벡터 인덱스는 [03-vector-index](../03-vector-index/README.md) 참고

## 하위 노트

- [01-embedding-basics](./01-embedding-basics.md): bi-encoder 원리, sparse와 비교, 유사도 척도와 정규화 손계산, 인코딩할 때 주의할 점
- [02-model-selection](./02-model-selection.md): 모델 고르는 기준, 공개 순위표의 한계, 골든셋으로 비교하는 방법, sparse와 dense를 함께 보는 법

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 모델 선택 기준 | 골든셋 dev 세트 Recall@5 (공개 순위표는 후보 거르기에만) | 한국어 법령은 공개 순위표와 다를 수 있음 |
| 후보 수 | 3~4개 (다국어 범용, 다국어 + 긴 입력, 한국어 특화) | 비교 비용 대비 충분 |
| 비교 시 인덱스 | Flat (정확 검색) | 인덱스 근사 오차를 모델 차이와 분리 |
| 척도 | 모델 권장 척도. 정규화 후 코사인(= 내적) 기본 | 정규화하면 척도 간 순위가 같아짐 |
| 입력 구성 | 법령명 + 조문 제목 + 본문 | 맥락 제공. 본문만 넣은 경우와 비교 |
| 청크 | sparse와 같은 조문 단위. 최대 입력 길이를 넘으면 나눔 | sparse와 같은 단위로 비교 |
| 실행 | 로컬 실행 우선 | 데이터 외부 전송 제약 |

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| 문서 집합 버전 | - |
| 골든셋 버전 | - |
| 모델 이름 / 버전, 차원, 최대 길이 | - |
| 정규화, 척도, 접두어 규칙 | - |
| 입력 구성 (제목 포함 여부) | - |
| 인덱스 | Flat |
| 잘림 비율 | - |

## 결과: 기준선

| 모델 | Recall@5 | Recall@10 | MRR | nDCG@10 | Recall@5 (user) | Recall@5 (expert) | 질의 인코딩 지연 | 저장 크기 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BM25 (비교용) | - | - | - | - | - | - | - | - |
| 후보 1 | - | - | - | - | - | - | - | - |
| 후보 2 | - | - | - | - | - | - | - | - |
| 후보 3 | - | - | - | - | - | - | - | - |

### sparse와 dense 질의별 비교 (선택한 모델 vs BM25)

| | dense 성공 | dense 실패 |
| --- | --- | --- |
| BM25 성공 | - | - |
| BM25 실패 | - | - |

- 대각선 밖(한쪽만 성공) 비율이 하이브리드 효과의 상한을 가늠하게 한다.

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 인코딩 [`encoder.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/encoder.py), 검색 [`hybrid.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/retrieval/hybrid.py), 비교 실행 [`eval.py`](https://github.com/Aegith-Ha/LawLens/blob/main/scripts/eval.py)
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `sentence-transformers`, `FlagEmbedding` (bge-m3)

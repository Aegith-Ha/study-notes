# 하이브리드 검색 (Hybrid Search)

BM25와 dense 검색 결과를 합쳐, 정확 일치(BM25)와 의미 유사(dense)를 모두 잡는 방법을 정리한다. 기본 RAG 실패 유형 중 F1(표현 불일치)과 F2(정확 일치 실패)를 고친다. 이 README에는 메인 결정과 결과를 두고, 합치기 방법과 조정 방법은 하위 노트에 둔다.

- 기준선은 [02-retrieval-basics](../../02-retrieval-basics/README.md), 지표는 [03-evals/01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md) 참고

## 하위 노트

- [01-fusion-methods](./01-fusion-methods.md): 가중합과 RRF, 정규화 방식, 손계산 예시(min-max의 함정, α 민감도, RRF), 합치기 전 후보 수
- [02-tuning-and-analysis](./02-tuning-and-analysis.md): 효과 상한 가늠하기, 조정 순서, 말투·소스별로 나눠 보기, 질의별 변화 분석

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 기본 방법 | RRF (k = 60) | 정규화 불필요, 튜닝할 것이 적어 작은 dev 세트에서도 안전 |
| 후보 수 | 각 검색기 top-20, top-50과 비교 | 한쪽 하위권 문서도 합쳐지도록 |
| 가중합 | min-max / z-score × α 격자로 비교. RRF보다 유의하게 나을 때만 채택 | 과적합 방지 |
| 비교 기준 | BM25 단독, dense 단독 대비 Recall@5, MRR | 하이브리드가 두 기준선을 모두 넘어야 함 |
| 필수 확인 | `expert` 질의에서 BM25 단독 이상, "성공 → 실패" 질의 목록 | 평균에 가려진 하락 방지 |

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| 골든셋 버전 | - |
| BM25 설정, dense 모델·인덱스 | - (02-retrieval-basics 기준선과 동일) |
| 합치기 방법, k 또는 α, 정규화 | - |
| 후보 수 N | - |

## 결과

| 설정 | Recall@5 | MRR | nDCG@10 | Recall@5 (user) | Recall@5 (expert) | 실패 → 성공 | 성공 → 실패 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BM25 (기준선) | - | - | - | - | - | - | - |
| dense (기준선) | - | - | - | - | - | - | - |
| RRF, N = 20 | - | - | - | - | - | - | - |
| RRF, N = 50 | - | - | - | - | - | - | - |
| 가중합 (최적 α = -) | - | - | - | - | - | - | - |

- 실패 → 성공, 성공 → 실패는 BM25 기준선 대비 질의 수다.

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 가중 RRF 합치기 [`hybrid.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/retrieval/hybrid.py) (k=30, dense 0.6. 설정 근거는 [`README.md`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/README.md))
- 실행 방법은 연결된 프로젝트 README 참고
- 참고: 벡터 DB 내장 하이브리드 검색(Milvus hybrid search 등), `ranx` (fusion 함수 지원)

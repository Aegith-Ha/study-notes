# 검색 평가 지표 (Retrieval Metrics)

검색 결과를 점수로 바꾸는 방법을 정리한다. 이 README에는 두 지표 계열의 비교, 메인 지표 결정, 실험 결과를 두고, 지표별 설명은 하위 노트에 둔다.

- 골든셋을 만드는 방법은 [03-golden-set](../03-golden-set/README.md) 참고
- 답변 품질 평가는 `02-generation-metrics`에서 다룬다
- judge 설계와 검증은 `04-llm-judge`에서 다룬다

## 하위 노트

- [01-reference-based](./01-reference-based.md): 정답 기반 지표 (Recall@k, MRR, nDCG 등). 정의, 손계산 예시, 설계 판단
- [02-reference-free](./02-reference-free.md): 정답 없는 지표 (Context Relevance, Sufficiency 등). LLM judge 판정, 한계, 정답 기반 지표와 맞춰 보기

## 두 지표 계열 비교

| 항목 | 정답 기반 | 정답 없음 |
| --- | --- | --- |
| 필요한 것 | 질문 + 정답 목록(qrels) | 질문 + LLM judge |
| 주요 지표 | Recall@k, Precision@k, MRR, nDCG@k | Context Relevance@k, Context Sufficiency@k, Judge nDCG@k |
| Recall 측정 | 가능 | 불가 (Sufficiency로 근사) |
| 신뢰도 좌우 요소 | 골든셋 품질 (누락, 판정 기준) | judge 품질 (편향, 모델 버전) |
| 적용 범위 | 골든셋 질의 (50~200개) | 모든 질의 |
| 비용 | 계산은 거의 무료, 골든셋 구축 비용이 큼 | 질의마다 judge 호출 비용 |
| 주로 쓰는 단계 | 기법 비교, 회귀 테스트 | 운영 모니터링, 골든셋 후보 판정 |

- 두 계열의 절댓값은 섞어서 비교하지 않는다. 정답 없는 지표가 보통 더 높게 나온다.
- 기준은 정답 기반 지표로 정하고, 정답 없는 지표는 정답 기반 지표와 순위가 일치하는 것을 확인한 뒤 골든셋 밖에서 쓴다.

## 메인 지표 (초안)

| 용도 | 계열 | 지표 | 이유 |
| --- | --- | --- | --- |
| 기준 지표 | 정답 기반 | **Recall@5** | LLM 컨텍스트에 근거가 들어오는지가 답변 품질의 전제 |
| 순위 품질 | 정답 기반 | nDCG@10 | 등급 판정 골든셋일 때, 리랭커 효과 확인 |
| 1차 검색 후보 | 정답 기반 | Recall@50 | 리랭커가 살릴 수 있는 상한 |
| 실패 분석 | 정답 기반 | Recall@5 = 0 질의 수 | 평균에 가려지는 완전 실패 확인 |
| 골든셋 밖 / 운영 | 정답 없음 | Context Relevance@5, Sufficiency@5 | 골든셋이 닿지 않는 질의의 검색 품질 추적 |

- k = 5는 컨텍스트 청크 수 기준 가정이다. 프로젝트 설정이 정해지면 맞춰 수정한다.
- 이후 `03-advanced-rag`의 모든 비교는 이 표의 정답 기반 지표를 기준으로 한다.

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| 골든셋 버전 | - (질문 수, 생성일) |
| 판정 단위 | 문서 (청크 → 문서 매핑, 중복 제거) |
| 판정 등급 | - (이진 / 0·1·2) |
| nDCG gain | 선형 |
| 검색기 | - (예: BM25, 운영 검색기) |
| 인덱스 설정 | - (청크 크기, 토크나이저 등) |
| judge 모델 / 프롬프트 버전 | - |
| judge temperature, 판정 질의 수 | - |

## 결과: 기준선

### 정답 기반

| 검색기 | Recall@1 | Recall@5 | Recall@10 | Recall@50 | MRR | nDCG@10 | Judged@10 | Recall@5 = 0 질의 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BM25 | - | - | - | - | - | - | - | - |

### 정답 없음

| 검색기 | Context Relevance@5 | Sufficiency@5 | Judge nDCG@5 |
| --- | --- | --- | --- |
| BM25 | - | - | - |

### 두 계열 일치도

| 확인 | 값 |
| --- | --- |
| judge 등급과 qrels 등급 일치율 / Cohen's kappa | - |
| 검색기 순위 일치 (Kendall's tau) | - (검색기 2개 이상 비교 후) |

- 이 결과가 `03-advanced-rag` 기법 비교의 출발점이 된다.

## 관련 코드

- 지표 계산 코드, judge 프롬프트: - (프로젝트 등록 후 [99-projects](../../99-projects/README.md)를 거쳐 링크)
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `ranx`, `pytrec_eval`, `ir-measures` (Judged@k 지원)

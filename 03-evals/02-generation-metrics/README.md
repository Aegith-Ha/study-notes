# 생성 평가 지표 (Generation Metrics)

검색된 컨텍스트로 만든 답변을 점수로 바꾸는 방법을 정리한다. 이 README에는 검색 평가와의 차이, 두 지표 계열의 비교, 검색 평가와 분리하는 방법, 메인 지표 결정을 두고, 지표별 설명은 하위 노트에 둔다.

- 검색 평가는 [01-retrieval-metrics](../01-retrieval-metrics/README.md) 참고
- 골든셋을 만드는 방법은 [03-golden-set](../03-golden-set/README.md) 참고
- judge 설계와 검증은 [04-llm-judge](../04-llm-judge/README.md)에서 다룬다

## 하위 노트

- [01-reference-based](./01-reference-based.md): 정답 기반 지표 (EM, Token F1, Answer Correctness, Citation 등). 정의, 손계산 예시, 설계 판단
- [02-reference-free](./02-reference-free.md): 정답 없는 지표 (Faithfulness, Answer Relevance, Citation Support 등). LLM judge 판정, 한계, 정답 기반 지표와 맞춰 보기

## 검색 평가와의 차이

생성 지표는 LLM이 쓴 **답변**을 채점하고, 검색 지표([01-retrieval-metrics](../01-retrieval-metrics/README.md))는 검색기가 가져온 **문서 목록**을 채점한다.

| | 검색 지표 | 생성 지표 (이 폴더) |
| --- | --- | --- |
| 평가 대상 | 검색 결과 (문서·청크의 순위 목록) | 생성된 답변 (텍스트) |
| 묻는 것 | 필요한 근거를 가져왔나, 위쪽에 있나 | 답이 맞나, 근거에 충실한가 |
| 정답 형태 | 정답 문서 목록과 등급 (qrels) | 정답 답변, 정답 주장(claim) 목록 |
| 정답 기반 지표 | Recall@k, Precision@k, MRR, nDCG, MAP | EM, Token F1, Answer Correctness, Claim Recall, 인용 정확도 |
| 정답 없는 지표 (judge) | Context Relevance, Sufficiency, Judge nDCG | Faithfulness, Answer Relevance, Citation Support, 거절 |
| 점수가 낮으면 고칠 곳 | 검색기, 청킹, 하이브리드, 리랭커 | 프롬프트, 생성 모델, 컨텍스트 순서 |

- **결과물 종류로 나눈다.** 생성 지표는 LLM이 쓴 답변이나 요약이 결과물일 때 쓴다. 중간에 LLM을 써도 최종 결과가 문서 목록이면 생성 지표를 쓰지 않는다.
- **채점 대상이 답변이면 생성 지표다.** Faithfulness, Citation Support는 검색 결과를 함께 보지만 점수가 매겨지는 것은 답변이므로 이 폴더에 둔다.
- **정답 기반 / 정답 없음과는 다른 축이다.** 이 구분(검색 / 생성)은 폴더로, 정답 유무는 폴더 안의 파일(`01-reference-based`, `02-reference-free`)로 나눈다. 두 축을 합친 2×2 표는 [03-evals README](../README.md) 참고
- **RAG에서는 이어져 있다.** 답변은 검색 결과로 만들어지므로, 생성 점수가 낮으면 원인이 검색인지 생성인지 나눠야 한다. 방법은 아래 "검색 평가와 분리하기" 참고

| 시스템 | 검색 지표 | 생성 지표 |
| --- | --- | --- |
| 검색 결과만 보여 주는 검색 화면 | 사용 | 사용 안 함 |
| RAG (검색 + 답변) | 사용 (원인 진단용) | 사용 (최종 품질) |
| 검색 없이 LLM만 쓰는 답변 | 사용 안 함 | 사용 (Faithfulness처럼 컨텍스트가 필요한 지표는 제외) |

## 두 지표 계열 비교

| 항목 | 정답 기반 | 정답 없음 |
| --- | --- | --- |
| 필요한 것 | 질문 + 정답 답변 (+ 근거 문서) | 질문 + 검색된 컨텍스트 + LLM judge |
| 주요 지표 | Answer Correctness, Claim Recall, EM, Citation Recall | Faithfulness, Answer Relevance, Citation Support, Refusal |
| 측정하는 것 | 맞았는가 | 근거에 충실한가, 질문에 맞게 답했는가 |
| 놓치는 것 | 정답에 없는 환각 덧붙임 (정답과 모순되지 않으면) | 검색이 틀렸을 때의 충실한 오답 |
| 신뢰도 좌우 요소 | 정답 답변 품질, judge 품질 | judge 품질 (편향, 모델 버전) |
| 적용 범위 | 골든셋 질의 (50~200개) | 모든 질의 |
| 주로 쓰는 단계 | 생성 설정 비교, 회귀 테스트 | 환각 감시, 운영 모니터링 |

- 두 계열은 서로 대신하지 않는다. 맞았는지는 정답 기반으로, 환각은 Faithfulness로 따로 본다.
- 두 계열의 절댓값은 섞어서 비교하지 않는다.

## 검색 평가와 분리하기

생성 점수가 낮을 때 원인이 검색인지 생성인지 나눠 봐야 개선할 곳을 정할 수 있다.

### 컨텍스트 두 가지로 평가

| 평가 | 컨텍스트 | 보는 것 |
| --- | --- | --- |
| 생성기 단독 | 골든셋 근거 문서(oracle context)를 그대로 넣음 | 근거가 완벽할 때 생성기가 얼마나 잘 답하는가 (생성 상한) |
| 전체 파이프라인 | 실제 검색 결과 top-k를 넣음 | 사용자가 실제로 받는 답변 품질 |

- 두 점수의 차이가 검색 때문에 잃는 몫이다. 차이가 크면 [04-advanced-rag](../../04-advanced-rag/README.md)의 검색 기법이 우선이고, 생성기 단독 점수가 낮으면 프롬프트나 모델이 우선이다.

### 질의별 원인 나누기

검색 지표(Recall@5)와 생성 지표(Answer Correctness)를 질의마다 같이 보면 네 칸으로 나뉜다.

| | 답변 맞음 | 답변 틀림 |
| --- | --- | --- |
| **검색 성공** (Recall@5 > 0) | 정상 | **생성 문제**: 근거를 받고도 틀림 → 프롬프트, 모델 |
| **검색 실패** (Recall@5 = 0) | **확인 필요**: 근거 없이 맞음 → 모델 사전 지식 또는 우연. Faithfulness 확인 | **검색 문제** → 검색 기법 |

- "검색 실패 + 답변 맞음"은 좋은 결과가 아니다. 문서가 바뀌면 틀릴 수 있는 답변이다.
- 칸별 질의 수를 결과에 함께 기록한다.

## 메인 지표 (초안)

| 용도 | 계열 | 지표 | 이유 |
| --- | --- | --- | --- |
| 기준 지표 | 정답 기반 | **Answer Correctness** (전체 파이프라인) | 사용자가 받는 답이 맞는가 |
| 생성 상한 | 정답 기반 | Answer Correctness (oracle context) | 검색과 생성 문제 분리 |
| 환각 | 정답 없음 | **Faithfulness** | 정답 기반 지표가 못 보는 근거 없는 내용 |
| 단답형 보조 | 정답 기반 | 정규화 후 EM | judge 없이 빠르게 확인 |
| 거절 | 정답 기반 | 답 없음 질의 거절 정확도, 과잉 거절률 | 무조건 답하거나 무조건 거절하는 설정 걸러내기 |
| 골든셋 밖 / 운영 | 정답 없음 | Faithfulness, Answer Relevance, Refusal Appropriateness | 골든셋이 닿지 않는 질의의 답변 품질 추적 |

- 이후 프롬프트, 모델, 컨텍스트 구성 비교는 이 표의 기준 지표와 Faithfulness를 함께 본다.

## 관련 코드

- 생성, 지표 계산 코드, judge 프롬프트: - (lawlens의 답변 생성이 아직 구현 전. 구현되면 [99-projects/01-lawlens](../../99-projects/01-lawlens.md)를 거쳐 링크)
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `ragas`, `deepeval` (Faithfulness, Answer Relevance 등 구현 포함. 지표 정의와 프롬프트가 라이브러리마다 다르므로 버전을 기록한다)

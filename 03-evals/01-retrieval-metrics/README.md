# 검색 평가 지표 (Retrieval Metrics)

검색 결과를 점수로 바꾸는 방법을 정리한다. 이 README에는 생성 평가와의 차이, 두 지표 계열의 비교, 메인 지표 결정을 두고, 지표별 설명은 하위 노트에 둔다.

- 골든셋을 만드는 방법은 [03-golden-set](../03-golden-set/README.md) 참고
- 답변 품질 평가는 [02-generation-metrics](../02-generation-metrics/README.md)에서 다룬다
- judge 설계와 검증은 [04-llm-judge](../04-llm-judge/README.md)에서 다룬다

## 하위 노트

- [01-reference-based](./01-reference-based.md): 정답 기반 지표 (Recall@k, MRR, nDCG 등). 정의, 손계산 예시, 설계 판단
- [02-reference-free](./02-reference-free.md): 정답 없는 지표 (Context Relevance, Sufficiency 등). LLM judge 판정, 한계, 정답 기반 지표와 맞춰 보기

## 생성 평가와의 차이

검색 지표는 검색기가 가져온 **문서 목록**을 채점하고, 생성 지표([02-generation-metrics](../02-generation-metrics/README.md))는 LLM이 쓴 **답변**을 채점한다.

| | 검색 지표 (이 폴더) | 생성 지표 |
| --- | --- | --- |
| 평가 대상 | 검색 결과 (문서·청크의 순위 목록) | 생성된 답변 (텍스트) |
| 묻는 것 | 필요한 근거를 가져왔나, 위쪽에 있나 | 답이 맞나, 근거에 충실한가 |
| 정답 형태 | 정답 문서 목록과 등급 (qrels) | 정답 답변, 정답 주장(claim) 목록 |
| 정답 기반 지표 | Recall@k, Precision@k, MRR, nDCG, MAP | EM, Token F1, Answer Correctness, Claim Recall, 인용 정확도 |
| 정답 없는 지표 (judge) | Context Relevance, Sufficiency, Judge nDCG | Faithfulness, Answer Relevance, Citation Support, 거절 |
| 점수가 낮으면 고칠 곳 | 검색기, 청킹, 하이브리드, 리랭커 | 프롬프트, 생성 모델, 컨텍스트 순서 |

- **결과물 종류로 나눈다.** 쿼리 재작성이나 리랭킹에 LLM을 써도, 사용자에게 보이는 결과가 문서 목록이면 검색 지표로 평가한다. 생성 지표는 LLM이 쓴 답변이나 요약이 결과물일 때 쓴다.
- **정답 기반 / 정답 없음과는 다른 축이다.** 이 구분(검색 / 생성)은 폴더로, 정답 유무는 폴더 안의 파일(`01-reference-based`, `02-reference-free`)로 나눈다. 두 축을 합친 2×2 표는 [03-evals README](../README.md) 참고
- **RAG에서는 이어져 있다.** 생성 지표는 검색 결과로 만든 답변을 채점하므로, 답이 틀리면 검색 지표로 원인을 나눈다. 검색 Recall과 답변 정답 여부로 질의를 네 칸으로 나누는 방법은 [02-generation-metrics](../02-generation-metrics/README.md)의 "검색 평가와 분리하기" 참고

| 시스템 | 검색 지표 | 생성 지표 |
| --- | --- | --- |
| 검색 결과만 보여 주는 검색 화면 | 사용 | 사용 안 함 |
| RAG (검색 + 답변) | 사용 (원인 진단용) | 사용 (최종 품질) |
| 검색 없이 LLM만 쓰는 답변 | 사용 안 함 | 사용 |

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

## 메인 지표

| 용도 | 계열 | 지표 | 이유 |
| --- | --- | --- | --- |
| 기준 지표 | 정답 기반 | **Recall@5** | LLM 컨텍스트에 근거가 들어오는지가 답변 품질의 전제 |
| 순위 품질 | 정답 기반 | nDCG@10 | 등급 판정 골든셋일 때, 리랭커 효과 확인 |
| 1차 검색 후보 | 정답 기반 | Recall@50 (참고용) | 리랭커가 살릴 수 있는 상한. Pooling 깊이(20)보다 깊어 21위 아래는 미판정이므로 Judged@50과 함께 본다 |
| 실패 분석 | 정답 기반 | Recall@5 = 0 질의 수 | 평균에 가려지는 완전 실패 확인 |
| 다중 근거 | 정답 기반 | Set Recall@5 (다중 근거 질문만) | 근거 일부만 가져온 경우를 성공으로 세지 않기 |
| 골든셋 밖 / 운영 | 정답 없음 | Context Relevance@5, Sufficiency@5 | 골든셋이 닿지 않는 질의의 검색 품질 추적 |

- k = 5는 컨텍스트 청크 수 기준 가정이다. 프로젝트 설정이 정해지면 맞춰 수정한다.
- 청크 크기가 다른 설정끼리 비교할 때는 같은 토큰 예산의 Recall과 질의당 컨텍스트 토큰을 함께 본다([01-reference-based](./01-reference-based.md) 3.7).
- 이후 [04-advanced-rag](../../04-advanced-rag/README.md)의 모든 비교는 이 표의 정답 기반 지표를 기준으로 한다.

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 지표 [`metrics.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/scoring/metrics.py), 실행·집계 [`runner.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/scoring/runner.py), CLI [`eval.py`](https://github.com/Aegith-Ha/LawLens/blob/main/scripts/eval.py)
  - 정답 없는 검색 지표(judge)는 아직 없음
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `ranx`, `pytrec_eval`, `ir-measures` (Judged@k 지원)

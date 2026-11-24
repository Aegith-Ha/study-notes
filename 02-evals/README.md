# 02-evals

평가(Evals) 체계 (1순위)

검색 평가와 생성 평가를 분리하고, 골든셋·LLM judge·회귀 테스트까지 평가 체계를 갖춘다.

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| 01-retrieval-metrics | 검색 평가 지표: Recall@k, MRR, NDCG | 예정 |
| 02-generation-metrics | 생성 평가 지표: 정확성, 답변 관련성 | 예정 |
| [03-golden-set](./03-golden-set/README.md) | 실제 사용자 질문 로그 기반 골든셋 50~200개 구축 (정답 + 근거 문서) | 진행 중 |
| 04-llm-judge | LLM-as-judge 채점 기준(rubric) 설계, 사람 판단과의 일치도 검증 | 예정 |
| 05-regression-ci | 배포 전 평가셋 자동 실행, CI 회귀 테스트 연결 | 예정 |

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.

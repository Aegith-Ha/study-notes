# Agentic RAG

LLM이 검색 여부, 검색어, 반복 검색을 스스로 정하는 RAG를 정리한다. 고정 파이프라인으로 풀리지 않는 다중 근거 질문과 모호한 질문이 대상이다. 이 README에는 기본 선택과 이유를 두고, 구조와 평가 방법은 하위 노트에 둔다.

- 비교 기준은 [04-advanced-rag](../../04-advanced-rag/README.md)에서 채택한 고정 파이프라인
- 지표는 [03-evals](../../03-evals/README.md) 참고

## 하위 노트

- [01-agentic-retrieval](./01-agentic-retrieval.md): 기본 RAG와의 차이, 패턴(라우터, 반복 검색, 분해, 교정형), 기본 RAG로 충분한 경우, 자주 생기는 문제
- [02-trajectory-evaluation](./02-trajectory-evaluation.md): 최종 결과와 경로를 함께 재는 법, 과정 지표, 손계산 예시, 기본 RAG와 비교하는 법

## 기본 선택과 이유

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 도입 시점 | [04-advanced-rag](../../04-advanced-rag/README.md) 고정 파이프라인 개선 후, 남은 실패가 다중 근거·모호한 질문일 때 | 단순한 질문에는 비용만 늘림 |
| 패턴 | 교정형 반복 검색 (충분성 판정 → 재검색 → 그래도 없으면 거절) | 다중 근거와 답 없음 질문을 함께 다룸 |
| 충분성 판정 | 평가용 Context Sufficiency judge와 같은 기준 문장 | 평가와 동작 기준 일치 |
| 검색 필수 규칙 | 문서 근거가 필요한 질문은 최소 1회 검색 | 사전 지식으로 답하는 것 방지 |
| 상한 | 최대 검색 3회, 질의당 토큰 예산 | 무한 반복, 비용 폭주 방지 |
| 중복 방지 | 이전 검색어와 결과 요약을 매 단계 제시 | 같은 검색 반복 방지 |
| 평가 | 최종 지표 + 과정 지표 + 답변 유형별 비교 | 평균에 가려진 손익 확인 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 에이전트 루프 [`loop.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/agent/loop.py)는 Phase 3 자리만 있음
- 실행 방법은 연결된 프로젝트 README 참고

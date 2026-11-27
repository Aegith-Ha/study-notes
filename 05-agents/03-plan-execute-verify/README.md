# 계획-실행-검증 루프 (Plan-Execute-Verify)

여러 도구를 순서대로 써야 하는 작업에서 에이전트가 계획하고, 실행하고, 결과를 검증하며, 실패하면 복구하거나 재계획하는 구조를 정리한다. 이 README에는 기본 선택과 이유를 두고, 루프 설계와 실패 복구는 하위 노트에 둔다.

- 도구는 [02-tool-calling-mcp](../02-tool-calling-mcp/README.md), 경로 평가는 [01-agentic-rag/02-trajectory-evaluation](../01-agentic-rag/02-trajectory-evaluation.md) 참고

## 하위 노트

- [01-loop-design](./01-loop-design.md): 패턴(ReAct, 계획 후 실행, 계획-실행-검증), 검증 방법(규칙, 도구, LLM), 멈추는 조건, 상태 관리, 언제 쓰나
- [02-failure-recovery](./02-failure-recovery.md): 실패 유형별 복구, 끝내는 방식(부분 결과), 실패 주입으로 복구 능력 평가와 손계산 예시

## 기본 선택과 이유

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 적용 대상 | 단계가 입력마다 달라지는 다단계 작업 (예: 계약서 조항과 사내 규정 대조) | 고정 단계면 워크플로가 더 싸고 안정적 |
| 패턴 | 계획-실행-검증, 단계마다 완료 기준 명시 | 틀린 중간 결과로 계속 진행하는 것 방지 |
| 검증 | 규칙 → 도구 재조회 → LLM 순으로 | 싸고 확실한 검증 먼저 |
| 멈추는 조건 | 최대 단계, 토큰 예산, 같은 실패 3회, 쓰기 동작 전 사람 확인 | 반복·비용·위험 통제 |
| 재시도 | 일시적 오류만, 간격을 늘려 최대 3회 | 같은 실패 반복 방지 |
| 실패 시 응답 | 부분 결과 + 실패 단계와 이유 | 실패를 숨긴 답변 방지 |
| 평가 | 작업 성공률, 과정 지표, 실패 주입 복구 성공률 | 정상 경로와 실패 경로 모두 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 루프 [`loop.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/agent/loop.py), 안전장치 [`policies.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/agent/policies.py)는 Phase 3 자리만 있음. 실패 주입 도구는 아직 없음
- 실행 방법은 연결된 프로젝트 README 참고

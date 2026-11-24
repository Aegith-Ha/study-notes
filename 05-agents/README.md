# 에이전트 확장 (Agents)

우선순위: 3순위

검색·도구 호출을 모델이 결정하는 구조로 확장한다.

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| [01-agentic-rag](./01-agentic-rag/README.md) | Agentic RAG (모델이 검색 여부·검색어·반복 검색을 결정) | 초안 |
| [02-tool-calling-mcp](./02-tool-calling-mcp/README.md) | function calling, MCP로 사내 DB/API 연결 | 초안 |
| [03-plan-execute-verify](./03-plan-execute-verify/README.md) | 계획 → 실행 → 검증 루프, 실패 복구 설계 | 초안 |

## 에이전트 평가: 결과와 과정

에이전트는 최종 결과뿐 아니라 거기까지 간 경로도 평가한다. 결과는 기존 지표를 그대로 쓰고, 과정 지표를 더한다.

| 대상 | 지표 | 위치 |
| --- | --- | --- |
| 최종 답변 | Answer Correctness, Faithfulness, 거절 정확도 | [03-evals/02-generation-metrics](../03-evals/02-generation-metrics/README.md) |
| 모은 근거 | 모든 단계 검색 결과 합집합의 Recall (본 문서 수 함께) | [03-evals/01-retrieval-metrics](../03-evals/01-retrieval-metrics/README.md) |
| 검색 경로 | 검색 횟수, 중복 검색률, 검색 판단 정확도 | [01-agentic-rag](./01-agentic-rag/02-trajectory-evaluation.md) |
| 도구 호출 | 도구 선택 정확도, 인자 정확 일치, 스키마 위반율 | [02-tool-calling-mcp](./02-tool-calling-mcp/01-function-calling.md) |
| 작업 | 작업 성공률, 부분 성공률, 실패 주입 복구 성공률 | [03-plan-execute-verify](./03-plan-execute-verify/02-failure-recovery.md) |
| 비용 | 질의당 LLM 호출 수, 토큰, 지연 | 각 주제 결과 표 |

- 에이전트 구조는 고정 파이프라인보다 비용이 크다. 평균이 아니라 **질문·작업 유형별**로 이득을 보고, 이득이 있는 유형에만 쓰는 라우팅을 함께 검토한다.
- 같은 입력에도 실행마다 경로가 달라질 수 있다. 회귀 테스트의 허용 폭(δ)은 반복 실행의 흔들림보다 크게 잡는다([05-regression-ci](../03-evals/05-regression-ci/01-gate-design.md) 5장).

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.

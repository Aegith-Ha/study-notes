# 운영 (LLMOps)

우선순위: 4순위

트레이싱, 비용, 보안, 피드백 루프 등 운영에 필요한 요소를 다룬다.

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| [01-tracing](./01-tracing/README.md) | 요청 단위 트레이싱 (Langfuse, Phoenix 등) | 초안 |
| [02-cost-optimization](./02-cost-optimization/README.md) | 프롬프트 캐싱, 시맨틱 캐시, 작은 모델 라우팅으로 비용 최적화 | 초안 |
| [03-security](./03-security/README.md) | 프롬프트 인젝션(간접 인젝션 포함), 문서 권한 제어, PII 처리 | 초안 |
| [04-feedback-loop](./04-feedback-loop/README.md) | 사용자 피드백 → 평가셋 → 개선으로 이어지는 루프 | 초안 |

## 운영 모니터링과 회귀 테스트

| 구분 | 회귀 테스트 ([03-evals/05-regression-ci](../03-evals/05-regression-ci/README.md)) | 운영 (이 섹션) |
| --- | --- | --- |
| 대상 질의 | 골든셋 (정답 있음) | 실제 사용자 질의 (정답 없음) |
| 시점 | 배포 전 | 배포 후 계속 |
| 지표 | 정답 기반 + 정답 없는 지표 | 정답 없는 지표 샘플, 지연·비용·오류, 피드백 |
| 연결 | 기준선 | 문제 사례 → [04-feedback-loop](./04-feedback-loop/README.md) → 골든셋 새 버전 |

- 모든 주제는 [01-tracing](./01-tracing/README.md)의 기록을 바탕으로 한다. 비용 측정, 보안 사고 추적, 피드백 원인 분석 모두 trace ID로 이어진다.

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.

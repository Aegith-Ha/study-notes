# 트레이싱 (Tracing)

요청 하나가 검색, 리랭크, LLM 호출, 도구 호출을 거치는 과정을 단계별로 기록하고, 이 기록으로 실패 원인과 지연·비용을 찾는 방법을 정리한다. 이 README에는 메인 결정과 결과를 두고, 설계와 도구·모니터링은 하위 노트에 둔다.

- 에이전트 경로 평가는 [05-agents/01-agentic-rag/02-trajectory-evaluation](../../05-agents/01-agentic-rag/02-trajectory-evaluation.md) 참고
- 운영 질의 품질 지표는 [03-evals/01-retrieval-metrics/02-reference-free](../../03-evals/01-retrieval-metrics/02-reference-free.md), [03-evals/02-generation-metrics/02-reference-free](../../03-evals/02-generation-metrics/02-reference-free.md) 참고

## 하위 노트

- [01-trace-design](./01-trace-design.md): trace와 span, 단계별로 남길 필드, 개인정보 처리, 지연 분해 손계산 예시
- [02-tools-and-monitoring](./02-tools-and-monitoring.md): 도구 비교(Langfuse, Phoenix, OpenTelemetry), 운영 대시보드 지표, 알림 기준, 샘플링

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 단위 | 요청 1건 = trace 1개, 단계마다 span | 실패 단계를 바로 찾음 |
| 필수 필드 | 버전(프롬프트·모델·인덱스·골든셋), 검색 결과 ID와 점수, 토큰, 지연, 오류 | 재현과 회귀 비교 |
| 원문 저장 | 질문·답변 원문은 마스킹 후 저장, 보관 기간 제한 | 개인정보 |
| 수집 범위 | 메타데이터(지연, 토큰, 오류)는 전부, 품질 judge는 샘플링 | judge 비용 통제 |
| 도구 | OpenTelemetry 형식으로 남기고 Langfuse 또는 Phoenix로 조회 | 도구 교체 쉬움 |
| 연결 | trace ID를 사용자 피드백과 함께 저장 | 피드백 → 원인 분석 ([04-feedback-loop](../04-feedback-loop/README.md)) |

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| 트레이싱 도구 / 버전 | - |
| 수집 기간, 요청 수 | - |
| 품질 judge 샘플링 비율, judge 모델 / 프롬프트 버전 | - |

## 결과

### 단계별 지연

| 단계 | p50 (ms) | p95 (ms) | 전체 대비 비율 (p50) |
| --- | --- | --- | --- |
| 쿼리 변환 | - | - | - |
| 검색 | - | - | - |
| 리랭크 | - | - | - |
| LLM 첫 토큰까지 | - | - | - |
| LLM 생성 | - | - | - |
| 전체 | - | - | - |

### 운영 지표

| 기간 | 요청 수 | 오류율 | 질의당 토큰 | 질의당 비용 | 샘플 Faithfulness | 샘플 Context Relevance |
| --- | --- | --- | --- | --- | --- | --- |
| - | - | - | - | - | - | - |

## 관련 코드

- 트레이싱 설정, 대시보드 정의: - (프로젝트 등록 후 [99-projects](../../99-projects/README.md)를 거쳐 링크)
- 실행 방법은 연결된 프로젝트 README 참고

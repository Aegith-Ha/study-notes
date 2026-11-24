# vLLM 서빙 (vLLM Serving)

오픈소스 LLM을 vLLM으로 직접 서빙할 때 알아야 할 원리(KV 캐시, PagedAttention, 연속 배칭)와 처리량·지연 측정, API 사용과의 비용 비교를 정리한다. 이 README에는 메인 결정과 결과를 두고, 원리와 측정 방법은 하위 노트에 둔다.

- 파인튜닝한 어댑터 서빙은 [03-lora-qlora/01-lora](../03-lora-qlora/01-lora.md) 4장 참고
- 운영 지표 수집은 [06-llmops/01-tracing](../../06-llmops/01-tracing/README.md) 참고

## 하위 노트

- [01-vllm-basics](./01-vllm-basics.md): KV 캐시와 메모리 손계산, PagedAttention, 연속 배칭, 접두어 캐시, 양자화, OpenAI 호환 API
- [02-serving-benchmark](./02-serving-benchmark.md): 지연(TTFT, TPOT)과 처리량, 동시 요청 수에 따른 변화, 손계산 예시, API와 비용 비교

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 도입 조건 | 데이터 외부 반출 불가, 또는 요청량이 많아 API보다 쌀 때 | 직접 서빙은 운영 부담이 큼 |
| API 형식 | OpenAI 호환 엔드포인트 | 앱 코드가 API 모델과 같은 형식 |
| 모델 | 7~8B, 필요 시 4-bit 양자화(AWQ/GPTQ) | GPU 한 장에서 KV 캐시 여유 확보 |
| 최대 길이 | RAG 입력에 맞춰 제한 (예: 8k) | 최대 길이가 크면 동시 처리 수가 줄어듦 |
| 접두어 캐시 | 켬 | 시스템 프롬프트 재사용 ([06-llmops/02-cost-optimization](../../06-llmops/02-cost-optimization/01-caching.md)) |
| 측정 | 실제 RAG 입력 길이 분포로 동시 요청 수를 바꿔 TTFT, TPOT, 처리량 | 짧은 입력 벤치마크는 실제와 다름 |
| 품질 확인 | 양자화·서빙 설정 변경 시 골든셋 회귀 테스트 | 서빙 설정도 품질을 바꿈 |

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| vLLM 버전, GPU / 메모리 | - |
| 모델 / 리비전, 양자화 | - |
| 최대 길이, GPU 메모리 사용 비율, 최대 동시 시퀀스 | - |
| 부하 조건 (입력·출력 길이 분포, 동시 요청 수) | - |
| GPU 시간당 비용, API 단가, 기준 날짜 | - |

## 결과

### 지연과 처리량

| 설정 | 동시 요청 | TTFT p50 / p95 | TPOT p50 | 요청 처리량 (req/s) | 출력 처리량 (tok/s) |
| --- | --- | --- | --- | --- | --- |
| bf16 | 1 / 8 / 32 | - | - | - | - |
| 4-bit | 1 / 8 / 32 | - | - | - | - |

### 품질과 비용

| 설정 | Answer Correctness | Faithfulness | 출력 100만 토큰당 비용 | 비교 API 비용 |
| --- | --- | --- | --- | --- |
| bf16 | - | - | - | - |
| 4-bit | - | - | - | - |

## 관련 코드

- 서빙 설정, 부하 테스트 스크립트: - (프로젝트 등록 후 [99-projects](../../99-projects/README.md)를 거쳐 링크)
- 실행 방법은 연결된 프로젝트 README 참고

# 긴 컨텍스트 vs RAG (Long Context vs RAG)

검색 없이 문서를 통째로 긴 컨텍스트에 넣는 방식과 RAG를 정확도, 비용, 지연으로 비교한다. "컨텍스트 창이 커졌는데 RAG가 아직 필요한가"에 이 프로젝트 데이터로 답하는 것이 목적이다. 이 README에는 메인 결정을 두고, 실험 설계와 비용 계산은 하위 노트에 둔다.

- 생성 지표는 [03-evals/02-generation-metrics](../../03-evals/02-generation-metrics/README.md) 참고
- RAG 쪽 설정은 [01-hybrid-search](../01-hybrid-search/README.md) ~ [04-chunking](../04-chunking/README.md)의 채택 설정 참고

## 하위 노트

- [01-experiment-design](./01-experiment-design.md): 비교할 설정(R / L / RL / O), 고정할 것, 측정 지표, 위치 실험(lost in the middle), 결과 해석
- [02-cost-latency](./02-cost-latency.md): 질의당 비용 공식, 입력 토큰 손계산(RAG 대비 21배), 프롬프트 캐싱 효과, 지연 구간, 판단 기준

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 비교 설정 | R(top-5), RL(top-50), L-oracle, L-검색, O | 긴 컨텍스트의 상한과 현실 성능을 나눠 봄 |
| 생성 모델 | 긴 컨텍스트를 지원하는 같은 모델로 모든 설정 | 모델 차이 제거 |
| 지표 | Answer Correctness, Claim Recall, Faithfulness, Citation Support, 질의당 토큰·비용, 첫 토큰 시간 p50/p95 | 정확도·충실도·비용·지연 |
| 위치 실험 | 정답 섹션을 앞 / 가운데 / 뒤에 두고 비교 | 긴 컨텍스트의 활용 한계 확인 |
| 판단 | 정확도 1%p당 추가 비용, 질문 유형별 결과 | 평균만으로 정하지 않음, 라우팅 가능성 확인 |
| 대상에서 제외 | 컨텍스트 창을 넘는 문서의 질문 (수 기록) | 공정 비교 |

## 관련 코드

- 설정별 실행, 토큰·비용 집계 스크립트: - (프로젝트 등록 후 [99-projects](../../99-projects/README.md)를 거쳐 링크)
- 실행 방법은 연결된 프로젝트 README 참고

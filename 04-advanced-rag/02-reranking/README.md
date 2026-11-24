# 리랭커 (Reranking)

1차 검색 후보를 cross-encoder로 다시 정렬해, 정답을 LLM에 넣는 top-5 안으로 끌어올리는 방법을 정리한다. 기본 RAG 실패 유형 중 F3(순위 문제)을 고친다. 이 README에는 메인 결정을 두고, 원리와 후보 수 정하기는 하위 노트에 둔다.

- 1차 검색은 [01-hybrid-search](../01-hybrid-search/README.md), 지표는 [03-evals/01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md) 참고

## 하위 노트

- [01-cross-encoder](./01-cross-encoder.md): bi-encoder와 cross-encoder, 리랭커 종류(모델, LLM pointwise·listwise), 비용과 지연, 입력 구성
- [02-candidate-depth](./02-candidate-depth.md): 1차 후보 수 N과 상한, 손계산 예시(리랭커가 살린 비율), Pooling 깊이와의 관계, 효과 평가 지표

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 1차 검색 | 하이브리드 채택 설정 고정 | 리랭커 효과만 분리 |
| 리랭커 | 다국어 cross-encoder 모델로 시작, LLM 리랭커는 비교용 | 로컬 실행, 지연 |
| 후보 수 N | 20 / 50 비교 | 상한과 지연의 균형 |
| 최종 k | 5 | 검색 메인 지표와 일치 |
| 점수 임계값 | 쓰지 않음 (top-5 고정) | 리랭커 점수는 순위용 |
| 필수 확인 | 리랭커가 밀어낸 질의 수, Judged@5, p95 지연 | 숨은 하락과 미판정 문서 확인 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 리랭크 단계 [`reranker.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/retrieval/reranker.py)는 아직 구현 전 (Phase 2 TODO)
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `sentence-transformers` (CrossEncoder), `FlagEmbedding` (bge-reranker)

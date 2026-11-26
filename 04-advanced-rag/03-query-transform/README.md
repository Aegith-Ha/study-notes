# 질의 변환 (Query Transform)

사용자 질문을 검색 전에 LLM으로 바꾸거나(재작성, 다중 질의, HyDE, 분해), 질문 속 조건을 뽑아 필터로 거는 방법을 정리한다. 기본 RAG 실패 유형 중 F4(모호한 질문), F5(조건 누락), F1(표현 불일치) 일부를 고친다. 이 README에는 메인 결정을 두고, 방법 설명은 하위 노트에 둔다.

- 기준 검색 설정은 [01-hybrid-search](../01-hybrid-search/README.md), [02-reranking](../02-reranking/README.md) 참고
- 중간 LLM 단계는 검색 지표로 평가한다 ([03-evals README](../../03-evals/README.md) 시스템 유형별 지표)

## 하위 노트

- [01-query-rewrite-hyde](./01-query-rewrite-hyde.md): 재작성, 다중 질의, HyDE, 분해. HyDE가 동작하는 이유, 위험(의도 이탈, 없는 용어), 평가
- [02-metadata-filter](./02-metadata-filter.md): 조건 추출 구조, 필드별 EM 평가, 과잉 추출과 결과 0건 처리, 검색 지표와 함께 보기, 식별자 질문의 정확 조회 라우팅

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 기본 방식 | 원래 질문 + 변환 질의를 각각 검색해 RRF로 합침 | 변환이 틀려도 원래 결과가 남음 |
| 비교 대상 | 재작성 / 다중 질의(3개) / HyDE | 방법별 효과와 비용 비교 |
| HyDE 적용 | dense 검색에만 | BM25에 가상 문서를 넣으면 없는 용어가 섞임 |
| 메타데이터 필터 | 확신도 높을 때만 필터, 낮으면 가산점, 결과 0건이면 필터 해제 | 틀린 필터는 정답을 완전히 지움 |
| 정확 조회 라우팅 | 식별자가 있으면 DB 조회 결과를 맨 앞에 두고 일반 검색 결과를 뒤에 붙임 | 번호 질문은 검색보다 조회가 정확. 오탐 대비로 검색 결과도 유지 |
| 평가 | 검색 지표(Recall@5, MRR) + 변환 품질(의도 이탈률, 필터 필드 EM) | 최종 효과와 원인 분리 |
| 나눠 보기 | `user` / `expert` 말투별 | 일상어 질문에서 효과가 클 것으로 예상 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 조문 번호·사건번호 질의를 DB 직접 조회로 보내는 라우팅 [`query.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/retrieval/query.py), 조문 인용 추출 [`references.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/parsing/references.py)
  - 쿼리 재작성, HyDE, 메타데이터 필터 추출은 아직 없음
- 실행 방법은 연결된 프로젝트 README 참고

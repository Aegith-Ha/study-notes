# 그래프·계층 기반 검색 (Graph and Hierarchical Retrieval)

청크를 따로따로 찾는 검색이 약한 두 종류의 질문을 다룬다. 여러 문서를 이어야 답이 나오는 질문(multi-hop)과 문서 전체를 아울러야 하는 질문(global)이다. 문서 사이의 연결을 그래프로 만들어 따라가는 방법과, 요약을 여러 단계로 쌓아 위에서 찾는 방법을 정리한다. 이 README에는 언제 필요한지와 기본 선택을 두고, 방법 설명은 하위 노트에 둔다.

- 기본 검색 설정은 [01-hybrid-search](../01-hybrid-search/README.md), [02-reranking](../02-reranking/README.md) 참고
- 더 가벼운 대안인 부모-자식 청크와 contextual retrieval은 [04-chunking](../04-chunking/README.md) 참고

## 하위 노트

- [01-graph-retrieval](./01-graph-retrieval.md): 참조 링크 확장(가벼운 그래프), GraphRAG의 개체·관계 그래프와 커뮤니티 요약, local / global 검색, 색인 비용, 평가
- [02-hierarchical-summary](./02-hierarchical-summary.md): RAPTOR 방식의 요약 트리, 트리 탐색과 전체 펼침 검색, 노드 수 손계산, 요약 환각과 갱신 비용, 평가

## 언제 필요한가

| 질문 유형 | 예 | 일반 검색의 문제 | 맞는 방법 |
| --- | --- | --- | --- |
| 단일 근거 | "환불 기한은?" | 없음 | 일반 검색 (이 폴더 불필요) |
| 참조를 따라가야 함 | "3.2항의 예외는 어디에 적용되나?" (3.2항이 3.1항을 참조) | 참조된 섹션은 질문과 단어가 안 겹쳐 못 찾음 | 참조 링크 확장 |
| 여러 문서 연결 (multi-hop) | "해외 배송 상품을 반품하면 누가 배송비를 내나?" (반품 정책 + 해외 배송 안내) | 두 문서 중 하나만 상위에 옴 | 그래프 검색, 질의 분해 ([03-query-transform](../03-query-transform/README.md)) |
| 전체를 아우름 (global) | "환불 관련 규정의 주요 변경점을 정리해 줘" | 어느 청크 하나에도 답이 없음 | 커뮤니티 요약(GraphRAG global), 요약 트리 |

- 먼저 골든셋에서 이 유형의 질문이 얼마나 되는지 센다(`answer_type = 다중 근거`, [03-golden-set](../../03-evals/03-golden-set/README.md) 질문 구성). 비율이 낮으면 이 폴더의 방법은 비용 대비 효과가 작다.

## 기본 선택과 이유

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 우선순위 | 다른 고급 기법(01~04) 이후. 다중 근거·전체 요약형 질문이 많을 때만 | 색인 비용이 크고, 대부분의 질문은 단일 근거 |
| 첫 시도 | 참조 링크 확장 (문서 안의 "3.2절 참조", "위 절차에 따라" 같은 참조를 그래프로) | 규칙으로 만들 수 있어 LLM 비용이 거의 없음 |
| 다음 시도 | 질의 분해와 비교한 뒤에 GraphRAG, 요약 트리 | 질의 분해가 더 싸고, 효과가 비슷하면 그쪽을 씀 |
| 평가 | 다중 근거 질문의 Set Recall@k, 전체 요약형은 pairwise judge(포괄성) | 문서별 Recall로는 연결 효과가 안 보임 |
| 인용 | 요약 노드를 근거로 인용하지 않고, 요약이 가리키는 원문 청크를 인용 | 요약에는 환각이 섞일 수 있음 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 문서 안의 참조(인용) 추출 [`references.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/parsing/references.py). 참조 링크 확장의 재료다
  - 그래프 검색, 요약 트리는 아직 없음
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 구현: Microsoft GraphRAG, LightRAG, LlamaIndex의 그래프·트리 인덱스, RAPTOR 공개 구현

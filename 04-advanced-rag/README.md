# 고급 RAG 기법 (Advanced RAG)

우선순위: 2순위

각 기법은 [03-evals](../03-evals/README.md) 지표로 기준선 대비 개선 폭을 비교한다. 기준선(BM25, dense, 기본 RAG)은 [02-retrieval-basics](../02-retrieval-basics/README.md)에서 만든다.

- 지표를 올리기 위해 바꿀 수 있는 것(레버)과 시도 순서는 [00-improvement-levers](./00-improvement-levers/README.md)에 모아 두었다. 아래 주제를 고르기 전에 먼저 본다.

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| [00-improvement-levers](./00-improvement-levers/README.md) | 지표 개선 레버 전체 개요: 레버 지도, 시도 순서, 실험 규칙 | 초안 |
| [01-hybrid-search](./01-hybrid-search/README.md) | 하이브리드 검색 (BM25 + 벡터) | 초안 |
| [02-reranking](./02-reranking/README.md) | 리랭커 (cross-encoder) 도입 | 초안 |
| [03-query-transform](./03-query-transform/README.md) | 쿼리 재작성, HyDE, 메타데이터 필터링 | 초안 |
| [04-chunking](./04-chunking/README.md) | 문서 구조 기반 청킹, 부모-자식 청크, contextual retrieval | 초안 |
| [05-document-parsing](./05-document-parsing/README.md) | 표 / PDF 레이아웃 / 이미지 문서 파싱 개선 | 초안 |
| [06-long-context-vs-rag](./06-long-context-vs-rag/README.md) | 긴 컨텍스트 vs RAG 비교 실험 (비용, 지연시간, 정확도) | 초안 |
| [07-graph-hierarchical](./07-graph-hierarchical/README.md) | 그래프 검색(참조 링크 확장, GraphRAG), 계층 요약 검색(RAPTOR) | 초안 |

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.

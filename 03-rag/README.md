# 03-rag

RAG 관련 개념 정리와 실습 기록 (찾은 문서로 답을 잘 만드는 기술)

- 목표: 검색한 문서를 근거로 LLM이 정확한 답변을 생성하게 한다.
- 평가 기준: 답변 정확성, faithfulness, answer relevance (+ context recall)
- 검색: [02-search-ir](../02-search-ir/)에서 학습한 retriever와 [Milvus](../00-infra/milvus/) collection을 사용한다.

```
query → retriever (02-search-ir) → chunk 선택 → prompt 구성 → LLM → 답변
```

## [00. Data](./00-data/)

RAG 실험용 데이터

- 긴 문서, 질문, 정답 답변 구성
- 근거 문서 정보 포함

## [01. Basics](./01-basics/)

1. [Naive RAG](./01-basics/01-naive-rag/) : retrieve → prompt → LLM 최소 동작 예제
2. [Prompt Template](./01-basics/02-prompt-template/) : context 넣는 방식과 출처 표기

## [02. Chunking](./02-chunking/)

답변 품질 기준의 문서 분할 전략

1. [Chunk Size](./02-chunking/01-chunk-size/) : chunk size, overlap에 따른 답변 변화
2. [Semantic Chunking](./02-chunking/02-semantic-chunking/) : 의미 단위 분할
3. [Parent-Child](./02-chunking/03-parent-child/) : small-to-big, 작게 검색하고 크게 전달
4. [Metadata](./02-chunking/04-metadata/) : 제목, 섹션 정보 추가

## [03. Retrieval Integration](./03-retrieval-integration/)

02-search-ir의 retriever를 RAG 파이프라인에 연결

1. [Top-k Context](./03-retrieval-integration/01-top-k-context/) : top-k와 context 길이 예산
2. [Query Rewrite](./03-retrieval-integration/02-query-rewrite/) : query 확장, HyDE, multi-query
3. [Hybrid Rerank](./03-retrieval-integration/03-hybrid-rerank/) : hybrid 검색과 rerank의 파이프라인 적용

## [04. Evaluation](./04-evaluation/)

1. [Retrieval Eval](./04-evaluation/01-retrieval-eval/) : context recall (02-search-ir 지표 재사용)
2. [Generation Eval](./04-evaluation/02-generation-eval/) : faithfulness, answer relevance
3. [LLM Judge](./04-evaluation/03-llm-judge/) : LLM을 이용한 답변 평가
4. [Failure Analysis](./04-evaluation/04-failure-analysis/) : 검색 실패와 생성 실패 구분

## [05. Advanced](./05-advanced/)

1. [Agentic RAG](./05-advanced/01-agentic-rag/)
2. [Graph RAG](./05-advanced/02-graph-rag/)

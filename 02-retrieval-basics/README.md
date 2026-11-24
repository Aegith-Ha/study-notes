# 검색 기초 (Retrieval Basics)

우선순위: 기초 (평가 체계와 고급 기법의 출발점)

sparse·dense 검색과 기본 RAG 파이프라인을 다룬다. 여기서 만든 검색기와 파이프라인이 [03-evals](../03-evals/README.md)에서 재는 **기준선**이 되고, [04-advanced-rag](../04-advanced-rag/README.md)의 모든 기법이 이 위에 올라간다.

```text
[기초 검색기]   sparse (BM25)          dense (임베딩 + 벡터 인덱스)      ← 이 폴더
                    └────────── 하이브리드 ──────────┘                ← 04-advanced-rag
                                    │
                         리랭커, 쿼리 변환, 청킹 ...                    ← 04-advanced-rag
```

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| [01-sparse-retrieval](./01-sparse-retrieval/README.md) | inverted index, TF-IDF, BM25와 변형(BM25+, BM25L, BM25F), 파라미터(k1, b), 토크나이저 | 초안 |
| [02-dense-retrieval](./02-dense-retrieval/README.md) | 임베딩 모델, 유사도 척도(코사인, 내적), 질의·문서 인코딩, 임베딩 모델 비교 | 초안 |
| [03-vector-index](./03-vector-index/README.md) | 근사 최근접 탐색(ANN): Flat, IVF, HNSW, PQ, 벡터 DB(Milvus 등) | 초안 |
| [04-naive-rag](./04-naive-rag/README.md) | 기본 RAG 파이프라인: 검색 top-k → 프롬프트 → 생성. 생성 평가의 기준선 | 초안 |

- 각 검색기는 [03-evals/01-retrieval-metrics](../03-evals/01-retrieval-metrics/README.md), 기본 RAG는 [03-evals/02-generation-metrics](../03-evals/02-generation-metrics/README.md)의 메인 지표로 잰다.

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.

# sparse 검색 (Sparse Retrieval)

단어 겹침으로 문서를 찾는 sparse 검색을 정리한다. BM25가 이 저장소의 첫 번째 검색 기준선이다. 이 README에는 메인 결정을 두고, 원리 설명은 하위 노트에 둔다.

- 평가 지표는 [03-evals/01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md) 참고
- dense 검색은 [02-dense-retrieval](../02-dense-retrieval/README.md), 둘을 섞는 하이브리드는 [04-advanced-rag/01-hybrid-search](../../04-advanced-rag/01-hybrid-search/README.md) 참고

## 하위 노트

- [01-inverted-index-tfidf](./01-inverted-index-tfidf.md): 역색인 구조, TF-IDF, 손계산 예시, 한국어 토큰화
- [02-bm25](./02-bm25.md): BM25 공식, 손계산 예시(TF-IDF와 순위 비교), 파라미터 k1·b 조정, 변형(BM25+, BM25L, BM25F), 학습된 sparse 두 종류(가중치만: bge-m3 sparse / 확장형: SPLADE)와 비교

## sparse 검색의 역할

| 강점 | 약점 | 보완 |
| --- | --- | --- |
| 문서 제목, 제품 코드, 고유명사, 숫자 정확 일치 | 바꿔 말한 표현, 동의어, 일상어 질문 ("결제했는데 돈이 안 돌아와요") | dense 검색, 하이브리드 |
| 학습 불필요, 빠름, 결과 이유 설명 가능 | 토큰화 품질에 크게 좌우됨 | 형태소 분석 + 사용자 사전 |

- 사용자 말투(`user`) 질문에서는 약하고 전문가 말투(`expert`) 질문에서는 강할 가능성이 높다. 골든셋의 `variant`별로 나눠서 본다([03-golden-set](../../03-evals/03-golden-set/README.md) 데이터 형식).

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 기준선 알고리즘 | BM25 (Lucene 방식 idf) | 사실상 표준, 라이브러리 지원이 넓음 |
| 파라미터 | k1 = 1.2, b = 0.75로 시작. dev 세트에서만 조정 | 기본값도 하나의 기준선 |
| 토큰화 | 형태소 분석(예: Kiwi) + 기능어 제거 + 도메인 용어 사용자 사전 | 한국어는 공백 기준이 거의 쓸모없음 |
| 색인 단위 | 골든셋 판정 단위와 맞춰 섹션 단위 | 청크 → 문서 매핑 없이 바로 비교 가능 |
| 비교 실험 | 토크나이저 3종(공백 / 형태소 / 2-gram), BM25 vs BM25F | 토큰화가 sparse 품질을 가장 크게 좌우 |
| 학습된 sparse | BM25와 별도 기준선으로 비교하고, 종류(가중치만 / 확장형)를 함께 기록. 하이브리드에 어느 쪽을 쓸지는 dev 세트로 결정 | 강약이 다르고, 같은 모델의 dense와는 실패가 겹치기 쉬움. 동의어 대응은 확장형만 기대할 수 있음 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): sparse 인코딩 [`encoder.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/encoder.py), 단일 방식 검색 [`hybrid.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/retrieval/hybrid.py)
  - lawlens의 sparse는 BM25가 아니라 bge-m3의 학습된 sparse 벡터다. 입력 토큰에만 가중치를 주는 방식이라 문서에 없는 단어로 확장하지 않는다. BM25 기준선은 따로 구현해야 한다.
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `rank_bm25`, `bm25s`, Elasticsearch / OpenSearch, Milvus full-text search, `kiwipiepy` (형태소 분석)

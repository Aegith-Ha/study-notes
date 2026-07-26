# 02-search-ir

정보 검색(IR) 관련 학습 기록 (문서를 잘 찾는 기술)

## [Sparse Retrieval](./sparse-retrieval/README.md)

문서와 query에 등장하는 단어를 기반으로 관련 문서를 찾는 전통적인 검색 방법을 학습한다.

1. [Inverted Index](./sparse-retrieval/01-inverted-index/README.md)
   - term dictionary와 posting list의 구조
   - AND/OR 검색과 positional inverted index 예제
2. [TF-IDF](./sparse-retrieval/02-tf-idf/README.md)
   - TF와 IDF를 이용한 단어 가중치 계산
   - cosine similarity 기반 문서 순위 계산 예제
3. [BM25](./sparse-retrieval/03-bm25/README.md)
   - BM25, BM25+, BM25L, BM25F의 원리와 차이
   - 검색 실행 및 모델별 점수 비교 예제
   - [BM25 실험 데이터](./sparse-retrieval/03-bm25/data/README.md): synthetic corpus, query, qrels 생성 방법

## [Evaluation](./evaluation/README.md)

검색 모델이 만든 문서 순위를 정답 데이터와 비교하고, 결과를 분석하는 방법을 학습한다.

1. [Qrels](./evaluation/01-qrels/README.md)
   - query별 정답 문서와 관련도 데이터 관리 및 검증
2. [Metrics](./evaluation/02-metrics/README.md)
   - Precision@k, Recall@k, MRR, nDCG의 개념과 계산
3. [Benchmarks](./evaluation/03-benchmarks/README.md)
   - 동일한 데이터와 조건에서 검색 모델별 성능 비교
4. [Reports](./evaluation/04-reports/README.md)
   - 평가 결과 요약과 분석 문서 관리
5. [Error Analysis](./evaluation/05-error-analysis/README.md)
   - 오검색과 미검색 사례 분류 및 개선 방향 기록

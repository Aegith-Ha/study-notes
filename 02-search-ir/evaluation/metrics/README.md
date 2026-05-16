# BM25 검색 평가

이 폴더는 BM25 계열 검색 결과를 qrels 기준으로 평가하는 스크립트를 담고 있다.

## 주요 파일

- `evaluate_metrics_bm25.py`: BM25, BM25+, BM25L, BM25F의 검색 품질을 비교 평가하는 CLI 스크립트

## 기본 실행

repo 루트(`/home/test0000/study-notes`)에서 실행한다.

```bash
python3 02-search-ir/evaluation/metrics/evaluate_metrics_bm25.py
```

기본값은 모든 모델을 `top-k=10` 기준으로 평가한다.

## 특정 모델만 평가

```bash
python3 02-search-ir/evaluation/metrics/evaluate_metrics_bm25.py \
  --model bm25f \
  --top-k 10
```

사용 가능한 모델:

- `all`
- `bm25`
- `bm25+`
- `bm25l`
- `bm25f`

## 데이터 파일 직접 지정

```bash
python3 02-search-ir/evaluation/metrics/evaluate_metrics_bm25.py \
  --docs 02-search-ir/bm25/data/generated/corpus.jsonl \
  --queries 02-search-ir/bm25/data/generated/queries.json \
  --qrels 02-search-ir/bm25/data/generated/qrels.json \
  --top-k 10
```

`corpus.jsonl`, `queries.json`, `qrels.json`이 없으면 기존 `bm25f_*` generated 파일을 fallback으로 사용한다.

## 출력 metric

- `P@k`: top-k 결과 중 relevant 문서 비율
- `R@k`: 전체 relevant 문서 중 top-k에서 찾은 비율
- `MRR@k`: 첫 번째 relevant 문서 순위의 역수
- `nDCG@k`: relevance 점수와 순위를 함께 반영한 ranking 품질

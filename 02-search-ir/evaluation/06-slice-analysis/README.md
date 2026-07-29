# Query Slice Analysis

전체 query의 평균 점수를 topic, intent, query 길이 같은 그룹으로 나누어 분석한다.

## 왜 필요한가?

전체 평균만 보면 특정 query 그룹에서 반복되는 약점을 놓칠 수 있다. 예를 들어 전체 Recall@10이 높더라도 자연어 질문이나 특정 topic에서만 점수가 낮을 수 있다.

Error analysis가 개별 실패 사례를 직접 확인한다면 slice analysis는 같은 특성을 가진 query들의 평균적인 경향을 찾는다.

## 분석 기준

`analyze_query_slices.py`는 benchmark JSON에 저장된 query별 metric과 metadata를 사용해 다음 기준으로 그룹을 만든다.

- `topic`: search, python, linux 같은 query 주제
- `intent`: topic lookup, keyword match 같은 검색 의도
- `query_length`: tokenizer 기준 `short (1-2)`, `medium (3-4)`, `long (5+)`

각 그룹에는 query 수와 평균 P@k, R@k, MRR@k, nDCG@k가 기록된다. query 수가 매우 작은 그룹은 일부 query의 영향을 크게 받을 수 있으므로 점수와 표본 수를 함께 확인한다.

## 사용법

먼저 여러 cutoff와 query별 결과가 포함된 benchmark JSON을 생성한다.

```bash
python 02-search-ir/evaluation/03-benchmarks/run_benchmark.py \
  --top-k 1 3 5 10 \
  --output 02-search-ir/evaluation/03-benchmarks/generated/bm25.json
```

BM25F의 `top-k=10` 결과를 topic별로 분석한다.

```bash
python 02-search-ir/evaluation/06-slice-analysis/analyze_query_slices.py \
  02-search-ir/evaluation/03-benchmarks/generated/bm25.json \
  --model bm25F \
  --top-k 10 \
  --slice-by topic \
  --output 02-search-ir/evaluation/06-slice-analysis/generated/bm25f-topic.json
```

`--model`을 생략하면 JSON의 첫 번째 모델을 사용하고, `--top-k`를 생략하면 가장 큰 cutoff를 사용한다. `--output`을 생략하면 JSON을 표준 출력으로 보여 준다.

## 해석 방법

1. 그룹별 query 수가 충분한지 확인한다.
2. 전체 평균과 차이가 큰 그룹을 찾는다.
3. 낮은 그룹의 query를 error analysis에서 직접 확인한다.
4. 원인에 대한 개선 가설을 세운 뒤 benchmark를 다시 실행한다.

Slice 점수는 문제 영역을 좁혀 주지만 성능 차이가 우연인지 알려 주지는 않는다. 모델 차이의 신뢰도는 `07-significance/`에서 query 단위 paired bootstrap으로 확인한다.

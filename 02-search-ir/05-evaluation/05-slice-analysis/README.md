# Query Slice Analysis

전체 query의 평균 점수를 topic, intent, query 길이 같은 그룹으로 나누어 분석한다.

## 왜 필요한가?

전체 평균만 보면 특정 query 그룹에서 반복되는 약점을 놓칠 수 있다. 예를 들어 전체 Recall@10이 높더라도 자연어 질문이나 특정 topic에서만 점수가 낮을 수 있다.

Error analysis가 개별 실패 사례를 직접 확인한다면 slice analysis는 같은 특성을 가진 query들의 평균적인 경향을 찾는다.

## 분석 기준

`analyze_query_slices.py`는 benchmark JSON에 저장된 query별 metric과 metadata를 사용해 다음 기준으로 그룹을 만든다.

- `topic`: search, python, linux 같은 query 주제
- `intent` (기본값): `keyword` / `paraphrase` query 유형
- `query_length`: tokenizer 기준 `short (1-2)`, `medium (3-4)`, `long (5+)`

각 그룹에는 query 수와 평균 P@k, R@k, MRR@k, nDCG@k가 기록된다. query 수가 매우 작은 그룹은 일부 query의 영향을 크게 받을 수 있으므로 점수와 표본 수를 함께 확인한다.

## BM25 결과 (nDCG@10)

| slice | 그룹 | query 수 | nDCG@10 |
| --- | --- | ---: | ---: |
| intent | keyword | 30 | 0.683 |
| intent | paraphrase | 30 | 0.000 |
| query_length | medium (3-4) | 20 | 0.635 |
| query_length | long (5+) | 40 | 0.195 |
| topic | korean_nlp | 10 | 0.468 |
| topic | linux | 10 | 0.405 |
| topic | database | 10 | 0.329 |
| topic | llm | 10 | 0.298 |
| topic | python | 10 | 0.288 |
| topic | search | 10 | 0.263 |

- **intent가 가장 큰 차이를 만든다.** 전체 평균 0.342는 0.683과 0.000의 평균이다.
- **query_length는 intent 차이가 다시 보이는 것이다.** paraphrase query는 문장형이라 대부분 5토큰 이상이다. 그래서 long 그룹이 낮은 이유는 길이 때문이 아니라 paraphrase가 몰려 있기 때문이다. 이처럼 두 속성이 함께 움직이면(confounding), 한 slice의 차이를 그 속성의 효과로 바로 해석하면 안 된다. 길이의 효과를 보려면 같은 intent 안에서 길이별로 나눠 봐야 한다.
- **topic 간 차이는 그룹당 query가 10개뿐이다.** 그래서 한두 query의 영향이 크다. 해석은 error analysis로 실제 사례를 확인한 뒤에 한다.

## 해석 방법

1. 그룹별 query 수가 충분한지 확인한다.
2. 전체 평균과 차이가 큰 그룹을 찾는다.
3. 낮은 그룹의 query를 error analysis에서 직접 확인한다.
4. 원인에 대한 개선 가설을 세운 뒤 benchmark를 다시 실행한다.

Slice 점수는 문제 영역을 좁혀 주지만 성능 차이가 우연인지 알려 주지는 않는다. 모델 차이의 신뢰도는 `06-significance/`에서 query 단위 paired bootstrap으로 확인한다.

## 실행 방법

먼저 여러 cutoff와 query별 결과가 포함된 benchmark JSON을 생성한다.

```bash
python 02-search-ir/05-evaluation/03-benchmarks/run_benchmark.py \
  --top-k 1 3 5 10 50 \
  --output 02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json
```

BM25의 `top-k=10` 결과를 intent별로 분석한다.

```bash
python 02-search-ir/05-evaluation/05-slice-analysis/analyze_query_slices.py \
  02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json \
  --model bm25 \
  --top-k 10 \
  --slice-by intent \
  --output 02-search-ir/05-evaluation/05-slice-analysis/generated/bm25-intent.json
```

`--model`을 생략하면 JSON의 첫 번째 모델을 사용하고, `--top-k`를 생략하면 가장 큰 cutoff를 사용한다. `--output`을 생략하면 JSON을 표준 출력으로 보여 준다.

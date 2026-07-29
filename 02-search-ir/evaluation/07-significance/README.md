# Statistical Significance

두 검색 모델의 평균 점수 차이가 query 표본에 따른 우연인지 query 단위 paired bootstrap으로 확인한다.

## 평균 delta만으로 부족한 이유

BM25F의 nDCG@10이 BM25보다 `0.01` 높더라도 일부 query가 만든 차이일 수 있다. 평균 delta는 변화의 크기를 보여 주지만 표본이 달라졌을 때 결과가 얼마나 흔들리는지는 보여 주지 않는다.

Paired bootstrap은 두 모델을 동일한 query로 평가했다는 짝지어진 구조를 유지하면서 query를 복원 추출한다. 각 표본에서 다음 delta를 다시 계산해 차이의 분포와 95% 신뢰구간을 만든다.

$$
\Delta metric = metric_{contender} - metric_{baseline}
$$

## 판정 기준

- 신뢰구간 전체가 `0`보다 큼: contender가 더 좋다는 근거가 있다.
- 신뢰구간 전체가 `0`보다 작음: baseline이 더 좋다는 근거가 있다.
- 신뢰구간이 `0`을 포함함: 현재 query 표본만으로 우열을 확정하기 어렵다.

통계적으로 유의하더라도 delta가 매우 작으면 실무적으로 중요한 개선이 아닐 수 있다. delta의 크기, latency, query slice, error case를 함께 확인한다.

## 사용법

먼저 query별 metric이 포함된 benchmark JSON을 생성한다.

```bash
python 02-search-ir/evaluation/03-benchmarks/run_benchmark.py \
  --top-k 1 3 5 10 \
  --output 02-search-ir/evaluation/03-benchmarks/generated/bm25.json
```

BM25를 baseline, BM25F를 contender로 두고 nDCG@10을 비교한다.

```bash
python 02-search-ir/evaluation/07-significance/compare_models.py \
  02-search-ir/evaluation/03-benchmarks/generated/bm25.json \
  --baseline bm25 \
  --contender bm25F \
  --metric ndcg \
  --top-k 10 \
  --samples 10000 \
  --seed 42 \
  --output 02-search-ir/evaluation/07-significance/generated/bm25-vs-bm25f.json
```

`--metric`은 `precision`, `recall`, `mrr`, `ndcg` 중 하나다. `--top-k`를 생략하면 benchmark의 가장 큰 cutoff를 사용한다. seed와 bootstrap 반복 횟수를 기록하면 같은 결과를 재현할 수 있다.

## 출력 항목

- baseline과 contender의 평균 점수
- `contender - baseline` delta
- 95% bootstrap 신뢰구간
- 신뢰구간이 `0`을 제외하는지 나타내는 `significant`
- `contender_better`, `baseline_better`, `inconclusive` 판정

이 분석은 현재 query 집합을 모집단의 대표 표본으로 가정한다. Query 수가 적거나 특정 유형에 편중되어 있으면 신뢰구간만으로 일반적인 검색 품질을 보장할 수 없다.

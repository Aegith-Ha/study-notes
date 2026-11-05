# Benchmarks

검색 모델을 같은 corpus, query, qrels, `top-k` 조건에서 실행해 성능을 비교하고, 결과를 보고서로 정리한다.

## Benchmark란?

Benchmark는 여러 모델을 같은 시험지로 평가하는 실험이다. BM25F의 점수가 BM25보다 높더라도 서로 다른 query나 `top-k`를 사용했다면 모델 차이라고 결론낼 수 없다. Benchmark의 핵심은 **비교하려는 요소 외의 조건을 같게 유지하는 것**이다.

이 예제에서는 [`00-data`](../../00-data/README.md)의 corpus를 한 번 로드해 index를 만들고, BM25 계열 모델만 바꾸어 같은 query를 검색한다. 모델별로 모든 query의 metric을 계산한 뒤 평균해 전체 점수를 만든다.

## 예제 소스

- [`run_benchmark.py`](./run_benchmark.py): BM25, BM25+, BM25L, BM25F를 같은 조건에서 평가하고 JSON 결과를 만든다.
- [`render_report.py`](./render_report.py): benchmark JSON을 모델별 지표 비교표가 있는 Markdown 보고서로 변환한다.

## 작동 원리

`run_benchmark.py`는 다음 순서로 작동한다.

1. corpus, queries, qrels를 로드한다.
2. corpus에서 BM25용 역색인과 BM25F용 필드 인덱스를 만든다.
3. query를 tokenize하고 모델별로 문서 score를 계산한다.
4. 가장 큰 `top-k`까지의 문서를 qrels와 비교한다.
5. 각 cutoff에서 query별 P@k, R@k, MRR@k, nDCG@k를 구한 뒤 산술 평균한다.
6. 모델별 평균, query별 점수, 검색 소요 시간을 JSON으로 출력한다.

소요 시간은 Python의 `perf_counter()`로 각 모델의 query 평가 구간만 측정한다. index 생성 시간은 포함하지 않으므로, 이 값은 전체 서비스 latency가 아니라 현재 예제의 상대적인 검색 비용을 비교하는 참고값이다.

JSON의 `per_query`에는 query별 지표와 함께 `topic`, `intent`, `concept_id`, `token_count`가 저장된다. 이 값은 [slice analysis](../05-slice-analysis/README.md)와 [significance](../06-significance/README.md)의 입력으로 쓰인다.

## 보고서: JSON을 Markdown으로 바꾸는 이유

Benchmark JSON은 프로그램이 다시 읽기 좋은 **machine-readable 산출물**이고, Markdown 보고서는 사람이 비교하기 좋은 **human-readable 산출물**이다.

### Baseline과 delta

Baseline은 새 모델을 비교하는 기준 모델이다. BM25를 baseline으로 두면 BM25F의 nDCG delta는 다음과 같다.

$$
\Delta nDCG = nDCG_{BM25F} - nDCG_{BM25}
$$

delta가 양수면 baseline보다 향상되었고, 음수면 낮아졌다는 뜻이다. 단, delta는 차이의 크기만 보여 줄 뿐 그 차이가 우연인지는 알려 주지 않는다. 그 판단은 [06-significance](../06-significance/README.md)에서 한다.

### 보고서를 읽는 순서

1. query/document 수와 cutoff 목록으로 비교 범위를 파악한다.
2. 목표에 가장 중요한 metric을 먼저 비교한다.
3. baseline 대비 delta로 변화 방향과 크기를 확인한다.
4. 품질이 높아진 대신 속도가 느려지지 않았는지 확인한다.
5. [05-slice-analysis](../05-slice-analysis/README.md)에서 어떤 query 그룹의 차이가 큰지 확인한다.
6. [06-significance](../06-significance/README.md)에서 delta의 95% 신뢰구간을 확인한다.
7. [04-error-analysis](../04-error-analysis/README.md)에서 점수 변화를 만든 실제 query 사례를 확인한다.

`render_report.py`는 수치와 비교표만 만든다. 왜 특정 모델이 더 좋았는지, 어떤 query 그룹에서 약한지는 실험자가 분석해 추가해야 한다.

## BM25 계열 결과

하단 [실행 방법](#실행-방법)의 명령으로 만든 보고서 중 `@10`과 `@50`만 옮긴 것이다(query 60개, 문서 500개).

| Model | k | P@k | R@k | MRR@k | nDCG@k | nDCG delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bm25 | 10 | 0.3700 | 0.1745 | 0.4417 | 0.3417 | +0.0000 |
| bm25+ | 10 | 0.4167 | 0.1953 | 0.4625 | 0.3503 | +0.0087 |
| bm25L | 10 | 0.4100 | 0.1924 | 0.4625 | 0.3464 | +0.0047 |
| bm25F | 10 | 0.3150 | 0.1469 | 0.4267 | 0.2831 | -0.0586 |
| bm25 | 50 | 0.2113 | 0.4793 | 0.4457 | 0.4197 | +0.0000 |
| bm25+ | 50 | 0.2133 | 0.4827 | 0.4663 | 0.4279 | +0.0082 |
| bm25L | 50 | 0.2127 | 0.4814 | 0.4663 | 0.4263 | +0.0066 |
| bm25F | 50 | 0.1957 | 0.4423 | 0.4295 | 0.3751 | -0.0446 |

- 전체 평균이라 keyword와 paraphrase가 섞여 있다. 유형별 점수는 [02-metrics](../02-metrics/README.md#bm25-baseline-결과)와 [05-slice-analysis](../05-slice-analysis/README.md)에서 본다.
- BM25+와 BM25L의 delta는 +0.005~0.009로 작다. 이 차이가 의미 있는지는 [06-significance](../06-significance/README.md)에서 확인한다.
- 이후 dense, hybrid, rerank 모델이 추가되면 이 표에 행을 늘려 같은 조건에서 비교한다.

## 실험 기록 항목

- 실험한 모델과 파라미터
- 사용한 corpus, query, qrels 버전 (`00-data`의 seed와 생성 스크립트)
- `top-k`와 평가 지표
- 실행 환경과 소요 시간
- 재현 명령어

## 재현 가능성을 높이는 방법

- corpus, query, qrels의 경로뿐 아니라 내용 버전을 기록한다.
- `top-k`, 모델 파라미터, tokenizer 버전을 고정한다.
- 실험 명령어와 Python 환경을 함께 남긴다.
- 속도는 warm-up 후 반복 측정하고 평균과 분산을 확인한다.

## 실행 방법

### Benchmark 실행

```bash
python 02-search-ir/05-evaluation/03-benchmarks/run_benchmark.py \
  --top-k 1 3 5 10 50 \
  --output 02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json
```

가장 큰 cutoff까지 검색을 한 번 수행하고 각 cutoff의 지표를 계산하므로 모델 검색을 반복하지 않는다. `--model bm25f`처럼 특정 모델만 실행할 수 있고, `--output`을 생략하면 JSON을 표준 출력으로 보여 준다.

### 보고서 변환

```bash
python 02-search-ir/05-evaluation/03-benchmarks/render_report.py \
  02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json \
  --output 02-search-ir/05-evaluation/03-benchmarks/generated/bm25.md
```

기본적으로 JSON의 첫 번째 모델을 baseline으로 쓴다. 다른 모델을 기준으로 비교하려면 `--baseline bm25F`처럼 지정한다.

`generated/`는 `.gitignore`에 포함되어 있다. 반복 실행해도 산출물이 git 변경 내역에 섞이지 않으며, 공유할 결과는 아래처럼 README에 정리한다.

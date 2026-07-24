# Benchmarks

검색 모델을 같은 corpus, query, qrels, `top-k` 조건에서 실행해 성능을 비교한다.

## Benchmark란?

Benchmark는 여러 모델을 같은 시험지로 평가하는 실험이다. BM25F의 점수가 BM25보다 높더라도 서로 다른 query나 `top-k`를 사용했다면 모델 차이라고 결론낼 수 없다. Benchmark의 핵심은 **비교하려는 요소 외의 조건을 같게 유지하는 것**이다.

이 예제에서는 corpus를 한 번 로드하고 index를 만든 뒤, BM25 계열 모델만 바꾸어 같은 query를 검색한다. 모델별로 모든 query의 metric을 계산한 후 평균해 전체 점수를 만든다.

## 작동 원리

`run_benchmark.py`는 다음 순서로 작동한다.

1. corpus, queries, qrels를 로드한다.
2. corpus에서 BM25용 역색인 인덱스와 BM25F용 필드 인덱스를 만든다.
3. query를 tokenize하고 모델별로 문서 score를 계산한다.
4. score가 높은 `top-k` 문서를 qrels와 비교한다.
5. query별 P@k, R@k, MRR@k, nDCG@k를 구한 뒤 산술 평균한다.
6. 모델별 점수와 검색 소요 시간을 JSON으로 출력한다.

산출 시간은 Python의 `perf_counter()`로 각 모델의 query 평가 구간을 측정한다. index 생성 시간은 포함하지 않으므로, 이 값은 전체 서비스 latency가 아니라 현재 예제의 상대적인 검색 비용을 비교하는 참고값이다.

## 실험 기록 항목

- 실험한 모델과 파라미터
- 사용한 corpus, query, qrels 버전
- `top-k`와 평가 지표
- 실행 환경과 소요 시간
- 재현 명령어

현재 BM25 계열 비교는 [`metrics/evaluate_metrics_bm25.py`](../metrics/evaluate_metrics_bm25.py)로 실행할 수 있다. 이 폴더에는 반복 가능한 실험 설정과 비교 기록을 저장한다.

## 예제 소스

- [`run_benchmark.py`](./run_benchmark.py): BM25, BM25+, BM25L, BM25F를 동일한 조건에서 평가하고 JSON 결과를 생성한다.

## 사용법

모든 BM25 모델을 `top-k=10`으로 비교한다.

```bash
python 02-search-ir/evaluation/benchmarks/run_benchmark.py \
  --output 02-search-ir/evaluation/benchmarks/generated/bm25.json
```

특정 모델과 `top-k`만 실험할 수도 있다.

```bash
python 02-search-ir/evaluation/benchmarks/run_benchmark.py \
  --model bm25f \
  --top-k 5
```

`--output`을 생략하면 JSON을 표준 출력으로 보여 준다. JSON에는 입력 파일, query/document 수, `top-k`, 모델별 지표와 소요 시간이 포함된다.

## 결과 해석

- P@k가 높으면 상위 결과에 오답이 적다는 뜻이다.
- Recall@k가 높으면 전체 정답 중 더 많은 문서를 `top-k`에서 찾았다는 뜻이다.
- MRR이 높으면 첫 정답이 빠르게 나온다는 뜻이다.
- nDCG가 높으면 관련도가 높은 문서가 더 위에 배치됐다는 뜻이다.

모델의 점수 차이가 작다면 query 샘플에 따른 우연일 수 있다. 실무에서는 query 그룹별 점수, 여러 번의 반복 측정, 통계적 유의성도 함께 확인한다.

## 재현 가능성을 높이는 방법

- corpus, query, qrels의 경로만 아니라 내용 버전을 기록한다.
- `top-k`, 모델 파라미터, tokenizer 버전을 고정한다.
- 실험 명령어와 Python 환경을 함께 남긴다.
- 속도는 warm-up과 반복 측정을 하고 평균과 분산을 확인한다.

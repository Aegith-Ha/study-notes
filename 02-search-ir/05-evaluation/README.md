# 05. Evaluation

검색 모델이 만든 문서 순위를 정답 데이터와 비교하고, 그 결과를 분석하는 방법을 학습한다.

## 검색 평가란?

검색 시스템은 query를 입력받아 관련성이 높은 문서부터 순서대로 반환한다. 검색 평가는 이 순서가 미리 정한 정답과 얼마나 일치하는지를 수치로 확인하는 과정이다.

예를 들어 `리눅스 로그 분석` query에 대해 장애 원인을 찾는 로그 분석 문서가 1위에 나오면 좋은 검색이다. 반면 리눅스나 로그라는 단어만 포함한 관련 없는 문서가 상위에 나오면 개선이 필요하다.

여기서는 실제 사용자 없이 고정된 query와 정답으로 평가하는 **offline evaluation**을 다룬다. 빠르고 재현하기 쉽지만, 클릭률이나 사용자 만족도를 직접 측정하는 online A/B test를 완전히 대체하지는 못한다.

- **Online A/B test**: 실제 사용자를 여러 집단으로 나누어 서로 다른 검색 모델을 제공하고 클릭률, 목표 달성률, 만족도 등의 차이를 비교하는 실험이다.

## 평가의 핵심 구성 요소

| 구성 요소 | 역할 | 이 프로젝트의 형식 |
| --- | --- | --- |
| Corpus | 검색 대상 문서 모음 | [`00-data`](../00-data/README.md)의 `corpus.jsonl` |
| Query | 사용자가 검색할 질문 | `queries.json` (keyword / paraphrase) |
| Qrels | query별 정답 문서와 관련도 | `qrels.json` |
| Retriever | query와 corpus로 순위를 만드는 모델 | BM25 계열, 이후 dense / hybrid / rerank |
| Metrics | 예측 순위와 qrels의 일치 정도 | P@k, R@k, MRR@k, nDCG@k |

query, corpus, qrels 중 하나라도 바뀌면 서로 다른 실험이 된다. 그래서 모델을 공정하게 비교하려면 입력 데이터, `top-k`, 평가 코드를 고정하고 모델만 바꿔야 한다. 02-search-ir의 모든 단계가 `00-data`를 공통으로 쓰는 이유다.

## 학습 순서

1. [Qrels](./01-qrels/README.md) : query별 정답 문서와 관련도 데이터 관리 및 검증
2. [Metrics](./02-metrics/README.md) : Precision@k, Recall@k, MRR, nDCG의 개념과 계산, BM25 baseline
3. [Benchmarks](./03-benchmarks/README.md) : 같은 데이터와 조건에서 모델 성능 비교, Markdown 보고서 생성
4. [Error Analysis](./04-error-analysis/README.md) : 오검색과 미검색 사례 분류
5. [Slice Analysis](./05-slice-analysis/README.md) : keyword query, paraphrase query 등 유형별 성능 비교
6. [Significance](./06-significance/README.md) : 모델 간 성능 차이의 paired bootstrap 신뢰구간

현재는 BM25 계열(BM25, BM25+, BM25L, BM25F)만 평가한다. dense, hybrid, rerank 모델은 해당 단계를 학습한 뒤 benchmark에 추가한다.

수치만 보면 어느 모델이 더 나은지는 알 수 있지만, 왜 나아졌는지는 알기 어렵다. benchmark와 metric은 전체 경향을 알려 주고, error analysis는 개별 실패의 원인을 찾는다. 두 가지를 함께 봐야 한다.

## 지금까지의 결론 (BM25 계열)

| 확인한 것 | 결과 | 근거 |
| --- | --- | --- |
| keyword query | nDCG@10 약 0.68~0.70, MRR@10 약 0.9 | [02-metrics](./02-metrics/README.md) |
| paraphrase query | 모든 모델 nDCG@10 약 0 | [05-slice-analysis](./05-slice-analysis/README.md) |
| BM25+ / BM25L vs BM25 | 평균은 높지만 유의하지 않음 | [06-significance](./06-significance/README.md) |
| BM25F vs BM25 | 유의하게 낮음 (필드 가중치 불일치) | [06-significance](./06-significance/README.md) |
| keyword 오검색 | 같은 주제의 다른 concept | [04-error-analysis](./04-error-analysis/README.md) |
| paraphrase 오검색 | 일반 단어만 겹친 다른 주제/무관 문서 | [04-error-analysis](./04-error-analysis/README.md) |

다음 단계인 [02. Dense Retrieval](../02-dense-retrieval/)의 목표는 paraphrase nDCG@10을 0에서 끌어올리는 것이다.

## 결과를 해석할 때 주의할 점

- 높은 점수는 현재 query와 qrels 범위에서만 좋다는 뜻이다.
- qrels에 정답이 누락되면 실제로는 좋은 문서도 오답으로 계산될 수 있다. `00-data`는 규칙으로 생성해 모든 쌍이 판정되어 있지만, 실무 데이터는 그렇지 않다.
- P@k, Recall@k, MRR, nDCG는 서로 다른 사용자 경험을 측정하므로 하나의 지표만으로 결론내리지 않는다.
- query 유형별로 성능이 크게 다를 수 있으므로 전체 평균만 보지 않는다. BM25의 nDCG@10은 keyword 0.68, paraphrase 0.00인데, 둘을 평균하면 0.34가 되어 두 유형의 차이가 가려진다.
- 소요 시간은 하드웨어, 캐시, 반복 횟수의 영향을 받으므로 품질 지표와 분리해 해석한다.

## 실행 방법

저장소 루트에서 `study-py312` 환경을 활성화한 뒤 실행한다.

```bash
conda activate study-py312
```

```bash
python 02-search-ir/05-evaluation/01-qrels/validate_qrels.py
```

```bash
python 02-search-ir/05-evaluation/02-metrics/evaluate_metrics_bm25.py --intent keyword --top-k 10 50
```

```bash
python 02-search-ir/05-evaluation/03-benchmarks/run_benchmark.py \
  --top-k 1 3 5 10 50 \
  --output 02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json
```

```bash
python 02-search-ir/05-evaluation/03-benchmarks/render_report.py \
  02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json \
  --output 02-search-ir/05-evaluation/03-benchmarks/generated/bm25.md
```

```bash
python 02-search-ir/05-evaluation/04-error-analysis/analyze_bm25_errors.py \
  --model bm25 --top-k 10 --intent paraphrase \
  --output 02-search-ir/05-evaluation/04-error-analysis/generated/bm25-paraphrase-errors.json
```

```bash
python 02-search-ir/05-evaluation/05-slice-analysis/analyze_query_slices.py \
  02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json \
  --model bm25 --top-k 10 --slice-by intent
```

```bash
python 02-search-ir/05-evaluation/06-significance/compare_models.py \
  02-search-ir/05-evaluation/03-benchmarks/generated/bm25.json \
  --baseline bm25 --contender bm25+ --metric ndcg --top-k 10
```

03 benchmark가 만든 JSON을 05와 06이 입력으로 쓴다. `02-metrics`는 지표만 따로 확인할 때 실행하고, 03과 04는 02의 계산 함수를 내부에서 import해 사용한다.

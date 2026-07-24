# 검색 평가

검색 모델의 품질을 측정하고 비교하기 위한 학습 및 실험 기록을 관리한다.

## 검색 평가란?

검색 시스템은 query를 입력받아 관련성이 높은 문서부터 순서대로 반환한다. 검색 평가는 이 순서가 사람이 미리 정한 정답과 얼마나 일치하는지를 수치로 확인하는 과정이다.

예를 들어 `리눅스 로그 확인`이라는 query에 대해 리눅스 로그 명령어를 설명한 문서가 1위에 나오면 좋은 검색이다. 반면 리눅스나 로그라는 단어만 포함한 관련 없는 문서가 상위에 나오면 개선이 필요하다.

이 예제는 사용자가 직접 접속하는 운영 환경이 아닌, 고정된 query와 정답으로 미리 평가하는 **offline evaluation**을 다룬다. 빠르고 재현하기 쉽지만, 클릭률이나 사용자 만족도를 직접 측정하는 online A/B test를 완전히 대체하지는 못한다.

## 평가의 핵심 구성 요소

| 구성 요소 | 역할 | 이 예제의 형식 |
| --- | --- | --- |
| Corpus | 검색 대상 문서 모음 | `corpus.jsonl` |
| Query | 사용자가 검색할 질문 | `queries.json` |
| Qrels | query별 정답 문서와 관련도 | `qrels.json` |
| Retriever | query와 corpus로 순위를 만드는 모델 | BM25, BM25+, BM25L, BM25F |
| Metrics | 예측 순위와 qrels의 일치 정도 | P@k, R@k, MRR@k, nDCG@k |

query, corpus, qrels 중 하나라도 바뀌면 서로 다른 실험이 된다. 그래서 모델을 공정하게 비교하려면 입력 데이터, `top-k`, 평가 코드를 고정하고 모델만 바꿔야 한다.

## Structure

- [qrels](./qrels/README.md): query와 정답 문서 사이의 관련도 정답 데이터 관리
- [metrics](./metrics/README.md): Precision@k, Recall@k, MRR, nDCG 등 평가 지표의 개념과 계산 코드
- [benchmarks](./benchmarks/README.md): 동일한 데이터와 조건에서 검색 모델별 성능 비교
- [reports](./reports/README.md): 평가 결과 요약과 분석 문서 관리
- [error-analysis](./error-analysis/README.md): 오검색과 미검색 사례를 분류하고 개선 방향 기록

## Evaluation flow

1. `qrels/`에서 평가용 정답을 정의한다.
2. `metrics/`에서 검색 결과를 평가할 지표와 계산 방법을 정의한다.
3. `benchmarks/`에서 검색 모델과 실험 조건을 고정하고 `metrics/`의 지표로 성능을 비교한다.
4. `reports/`에 모델별 성능과 해석을 정리한다.
5. `error-analysis/`에서 실패 사례와 개선 가설을 기록한다.

실제 실행에서는 `benchmarks/run_benchmark.py`가 `metrics/evaluate_metrics_bm25.py`의 계산 기능을 내부에서 사용하므로 metrics 스크립트를 먼저 별도로 실행할 필요는 없다. metrics 스크립트는 지표만 독립적으로 확인할 때 실행한다.

수치만 확인하면 어느 모델이 더 나은지는 알 수 있지만, 왜 나아졌는지는 알기 어렵다. 따라서 benchmark와 metric은 전체 경향을 알려 주고, error analysis는 개별 실패의 원인을 찾는 상호 보완적인 관계다.

## 결과를 해석할 때 주의할 점

- 높은 점수는 오직 현재 query와 qrels 범위에서 좋다는 뜻이다.
- qrels에 정답이 누락되면 실제로는 좋은 문서도 오답으로 계산될 수 있다.
- P@k, Recall@k, MRR, nDCG는 서로 다른 사용자 경험을 측정하므로 하나의 지표만으로 결론내리지 않는다.
- 소요 시간은 하드웨어, 캐시, 반복 횟수에 영향을 받으므로 품질 지표와 분리해 해석한다.

## 예제 실행 순서

저장소 루트에서 `study-py312` 환경을 활성화한 뒤 실행한다.

```bash
conda activate study-py312
python 02-search-ir/evaluation/qrels/validate_qrels.py
python 02-search-ir/evaluation/benchmarks/run_benchmark.py \
  --output 02-search-ir/evaluation/benchmarks/generated/bm25.json
python 02-search-ir/evaluation/reports/render_report.py \
  02-search-ir/evaluation/benchmarks/generated/bm25.json \
  --output 02-search-ir/evaluation/reports/generated/bm25.md
python 02-search-ir/evaluation/error-analysis/analyze_bm25_errors.py \
  --model bm25 \
  --output 02-search-ir/evaluation/error-analysis/generated/bm25-errors.json
```

`generated/`는 `.gitignore`에서 제외되므로 반복 실행해도 실험 산출물이 Git 변경 내역에 포함되지 않는다. 공유할 가치가 있는 결과만 별도의 Markdown 문서로 정리한다.

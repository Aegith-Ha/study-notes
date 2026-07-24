# Reports

평가 실험의 결과와 해석을 사람이 빠르게 비교할 수 있는 형태로 정리한다.

## 왜 JSON을 Markdown으로 변환하는가?

Benchmark JSON은 프로그램이 다시 읽고 처리하기 좋은 **machine-readable 산출물**이다. 하지만 여러 모델의 점수를 한눈에 비교하거나 실험 결론을 공유하기에는 불편하다. Markdown 보고서는 이 숫자를 표와 설명으로 바꾸는 **human-readable 산출물**이다.

보고서는 단순히 점수를 복사하는 문서가 아니다. 실험의 목적, 비교 기준, 성능이 바뀐 이유에 대한 가설, 한계를 함께 담아야 다른 사람이 올바르게 해석할 수 있다.

## Baseline과 delta

Baseline은 새 모델을 비교하는 기준 모델이다. 예를 들어 기본 BM25를 baseline으로 선택하면 BM25F의 nDCG delta는 다음과 같다.

$$
\Delta nDCG = nDCG_{BM25F} - nDCG_{BM25}
$$

delta가 양수면 baseline보다 향상되었고, 음수면 낮아졌다는 뜻이다. 단, delta는 차이의 크기만 보여 주며 그 차이가 통계적으로 유의한지는 알려 주지 않는다.

## 보고서 구성

- 실험 목적과 가설
- 데이터셋과 평가 조건
- 모델별 Precision@k, Recall@k, MRR, nDCG 결과
- 기준 모델 대비 변화량
- 결과 해석, 한계, 후속 실험

실험 설정은 `03-benchmarks/`에 두고, 이 폴더에는 요약 표와 분석 문서를 저장한다.

## 예제 소스

- [`render_report.py`](./render_report.py): benchmark JSON을 모델별 지표 비교표가 있는 Markdown 보고서로 변환한다.

### 변환 원리

`render_report.py`는 benchmark JSON의 `models`를 순회하며 P@k, R@k, MRR@k, nDCG@k, 소요 시간을 Markdown table의 한 행으로 변환한다. 선택한 baseline의 nDCG를 각 모델의 nDCG에서 빼 delta를 계산하고, 실험에 사용한 입력 파일 경로도 함께 기록한다.

## 사용법

먼저 benchmark JSON을 생성한 뒤 보고서로 변환한다.

```bash
python 02-search-ir/02-evaluation/03-benchmarks/run_benchmark.py \
  --output 02-search-ir/02-evaluation/03-benchmarks/generated/bm25.json

python 02-search-ir/02-evaluation/04-reports/render_report.py \
  02-search-ir/02-evaluation/03-benchmarks/generated/bm25.json \
  --output 02-search-ir/02-evaluation/04-reports/generated/bm25.md
```

기본적으로 JSON의 첫 번째 모델을 baseline으로 사용한다. 다른 모델과 nDCG 변화량을 비교하려면 `--baseline`을 지정한다.

```bash
python 02-search-ir/02-evaluation/04-reports/render_report.py \
  02-search-ir/02-evaluation/03-benchmarks/generated/bm25.json \
  --baseline bm25F
```

`--output`을 생략하면 Markdown을 표준 출력으로 보여 준다.

## 보고서를 읽는 순서

1. query/document 수와 `top-k`를 확인해 비교 범위를 파악한다.
2. 제품 목표에 가장 중요한 metric을 먼저 비교한다.
3. baseline 대비 delta로 변화 방향과 크기를 확인한다.
4. 품질이 높아진 대신 속도가 느려지지 않았는지 확인한다.
5. `05-error-analysis/`에서 점수 변화를 만든 실제 query 사례를 확인한다.

## 자동 보고서의 한계

`render_report.py`는 수치와 기초 비교표만 생성한다. 왜 특정 모델이 더 좋았는지, 운영에 적용할지, 어떤 query 그룹에서 성능이 낮은지는 실험자가 분석해 추가해야 한다.

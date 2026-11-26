# 평가 체계 (Evals)

우선순위: 1순위

검색 평가와 생성 평가를 분리하고, 골든셋·LLM judge·회귀 테스트까지 평가 체계를 갖춘다.

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| [01-retrieval-metrics](./01-retrieval-metrics/README.md) | 검색 평가 지표: Recall@k, MRR, NDCG | 초안 |
| [02-generation-metrics](./02-generation-metrics/README.md) | 생성 평가 지표: 정확성, 답변 관련성 | 초안 |
| [03-golden-set](./03-golden-set/README.md) | 골든셋 50~200개 구축 (정답 + 근거 문서). 기존 질의응답 데이터·상황 시나리오로 시작, 실제 사용자 로그로 확대 | 진행 중 |
| [04-llm-judge](./04-llm-judge/README.md) | LLM-as-judge 채점 기준(rubric) 설계, 사람 판단과의 일치도 검증 | 초안 |
| [05-regression-ci](./05-regression-ci/README.md) | 배포 전 평가셋 자동 실행, CI 회귀 테스트 연결 | 초안 |

## 지표 분류: 두 축

평가 지표는 서로 독립인 두 축으로 나눈다. 폴더(`01`, `02`)는 첫 번째 축, 각 폴더 안의 파일(`01-reference-based`, `02-reference-free`)은 두 번째 축이다.

| 축 | 나누는 기준 | 답하는 질문 |
| --- | --- | --- |
| 단계 (폴더) | 무엇을 채점하는가: 검색 결과(문서 목록) / 답변 | **어디서** 잘못됐나 → 고칠 위치 |
| 기준 (파일) | 무엇과 비교하는가: 미리 만든 정답 / 정답 없이 judge 판단 | **얼마나 믿을 수 있나, 어디까지 잴 수 있나** → 신뢰도와 적용 범위 |

| | **정답 기반** (정답과 비교) | **정답 없음** (judge가 그 자리에서 판단) |
| --- | --- | --- |
| **검색** (문서 목록 채점) | [Recall@k, MRR, nDCG](./01-retrieval-metrics/01-reference-based.md)<br>정답 문서를 가져왔나 | [Context Relevance, Sufficiency](./01-retrieval-metrics/02-reference-free.md)<br>가져온 문서가 질문과 관련 있어 보이나 |
| **생성** (답변 채점) | [Answer Correctness, EM, Citation Recall](./02-generation-metrics/01-reference-based.md)<br>정답과 같은 답인가 | [Faithfulness, Answer Relevance](./02-generation-metrics/02-reference-free.md)<br>가져온 문서에 충실한가, 질문에 맞게 답했나 |

- 네 칸은 서로 대신하지 않는다. 한 축의 지표만으로는 다른 축의 질문에 답할 수 없다.
- 헷갈리는 지표는 **채점되는 대상**으로 구분한다. Faithfulness, Citation은 검색 결과나 근거 문서를 보지만 점수가 매겨지는 것은 답변이므로 생성 지표다.
- 정답 없는 생성 지표는 검색 결과를 임시 기준으로 쓴다. 그래서 검색이 틀리면 충실한 오답이 만점을 받는다.

### 시스템 유형별로 쓰는 지표

단계 축은 시스템 유형이 아니라 **평가하는 결과물 유형**으로 나눈다. 검색 지표는 "찾기"를, 생성 지표는 "쓰기"를 평가한다. 하나의 시스템에 두 결과물이 모두 있을 수 있다.

| 시스템 | 결과물 | 쓰는 지표 |
| --- | --- | --- |
| 검색 서비스 (문서 목록만 보여 줌) | 문서 목록 | **검색만** |
| RAG (찾아서 답변 생성) | 문서 목록 + 답변 | **검색 + 생성 둘 다** |
| LLM 단독 (검색 없이 답변) | 답변 | **생성만** (Faithfulness처럼 컨텍스트가 필요한 지표는 제외) |

- RAG는 생성형이지만 생성 지표만 쓰지 않는다. 검색 지표를 함께 봐야 답변이 틀렸을 때 원인이 검색인지 생성인지 나눌 수 있다.
- 중간에 LLM(쿼리 재작성, 리랭킹)을 써도 최종 결과물이 문서 목록이면 검색 서비스로 본다. 결과를 사람이 읽는지 LLM이 읽는지에 따라 기준 지표가 달라진다 ([01-reference-based](./01-retrieval-metrics/01-reference-based.md) 3.1 참고).

### 두 지표를 함께 읽는 법

| 함께 보는 두 지표 | 같은 축 | 다른 축 | 의미 | 확인할 곳 |
| --- | --- | --- | --- | --- |
| 검색 정답 기반 Precision 낮음 / 검색 정답 없음 Context Relevance 높음 | 단계 (검색) | 기준 | 골든셋 누락 또는 judge가 관대함 | 골든셋, judge |
| 생성 정답 없음 Faithfulness 높음 / 생성 정답 기반 Correctness 낮음 | 단계 (생성) | 기준 | 충실한 오답. 정답 없는 지표의 구조적 한계 | 검색 Recall로 원인 확인 |
| 검색 정답 기반 Recall 높음 / 생성 정답 기반 Correctness 낮음 | 기준 (정답 기반) | 단계 | 근거를 받고도 틀림 | 프롬프트, 생성 모델 |
| 검색 정답 기반 Recall 낮음 / 생성 정답 기반 Correctness 낮음 | 기준 (정답 기반) | 단계 | 근거를 못 가져옴 | 검색기, 필터, 청킹 |

- 기준 축이 엇갈리면 **평가 도구**(골든셋, judge)를 먼저 의심하고, 단계 축이 엇갈리면 **시스템**(검색기, 생성기)을 의심한다.
- 질의별 원인 나누기 표는 [02-generation-metrics](./02-generation-metrics/README.md)의 "검색 평가와 분리하기" 참고

## 평가용 오픈소스 도구

지표 계산, judge 평가, 검증 통계, 골든셋 판정에 많이 쓰는 오픈소스와 라이브러리를 용도별로 정리한다. 위 표의 "평가 도구"(골든셋, judge)와 구분해서, 여기서는 그 작업을 돕는 소프트웨어를 말한다.

### 검색 지표 (정답 기반)

| 도구 | 특징 | 관련 노트 |
| --- | --- | --- |
| `trec_eval` | TREC 공식 C 도구. 다른 도구가 결과를 이 도구와 맞춘다 | [01-retrieval-metrics](./01-retrieval-metrics/01-reference-based.md) |
| `pytrec_eval` | trec_eval의 파이썬 래퍼. qrels와 검색 결과를 dict로 넣어 계산 | 위와 같음 |
| `ranx` | 빠르고 쓰기 쉬움. 여러 검색 결과 비교표, 유의성 검정, RRF 같은 결과 융합까지 지원 | 위와 같음, [04-advanced-rag/01-hybrid-search](../04-advanced-rag/01-hybrid-search/README.md) |
| `ir-measures` | 여러 백엔드를 하나의 인터페이스로. Judged@k, condensed 지표(nDCG′) 지원 | 위와 같음, [03-golden-set/02-pooling](./03-golden-set/02-pooling.md) |
| BEIR, MTEB | 공개 검색·임베딩 벤치마크. 모델 후보를 거를 때 순위표로 참고 | [02-retrieval-basics/02-dense-retrieval](../02-retrieval-basics/02-dense-retrieval/README.md) |

### RAG·생성 평가 프레임워크 (judge 기반 지표 포함)

| 도구 | 특징 | 관련 노트 |
| --- | --- | --- |
| `ragas` | RAG 전용. Faithfulness, Answer Relevance, Context Precision/Recall 등. 합성 테스트셋 생성 기능 | [02-generation-metrics](./02-generation-metrics/README.md), [03-golden-set/00-generation-methods](./03-golden-set/00-generation-methods.md) |
| `deepeval` | pytest처럼 테스트로 작성. RAG 지표, 기준표 기반 judge(G-Eval), CI 연결이 쉬움 | [05-regression-ci](./05-regression-ci/README.md) |
| `promptfoo` | YAML로 프롬프트·모델 비교와 회귀 테스트 작성. 공격(레드팀) 테스트 기능 | [05-regression-ci](./05-regression-ci/README.md), [06-llmops/03-security](../06-llmops/03-security/README.md) |
| TruLens | Context Relevance, Groundedness, Answer Relevance 중심. 실행 기록 추적 | [02-generation-metrics](./02-generation-metrics/02-reference-free.md) |
| Inspect | 평가 과제를 코드로 정의하는 범용 LLM 평가 프레임워크 | - |
| `lm-evaluation-harness` | 공개 벤치마크로 모델 자체를 평가. RAG 시스템 평가용은 아님 | - |

### 추적과 운영 모니터링 (평가 기능 포함)

| 도구 | 특징 | 관련 노트 |
| --- | --- | --- |
| Langfuse | 트레이싱, 데이터셋, judge 평가, 사람 점수 수집 | [06-llmops/01-tracing](../06-llmops/01-tracing/README.md) |
| Arize Phoenix | 트레이싱과 RAG 평가, 임베딩 시각화 | 위와 같음 |
| MLflow | `mlflow.evaluate`로 LLM 평가와 실험 기록 | - |

### judge 검증과 통계

| 도구 | 용도 | 관련 노트 |
| --- | --- | --- |
| `scikit-learn` | `cohen_kappa_score` (가중 kappa 포함) | [04-llm-judge/02-human-agreement](./04-llm-judge/02-human-agreement.md) |
| `krippendorff` | 판정자가 3명 이상이거나 빠진 판정이 있을 때의 일치도 | 위와 같음 |
| `scipy`, `statsmodels` | McNemar 검정, bootstrap | [05-regression-ci/01-gate-design](./05-regression-ci/01-gate-design.md) |

### 골든셋 판정(라벨링)

| 도구 | 특징 | 관련 노트 |
| --- | --- | --- |
| Label Studio | 범용 라벨링. 질문-문서 관련성 판정 화면을 직접 구성 | [03-golden-set/03-judging-and-review](./03-golden-set/03-judging-and-review.md) |
| Argilla | LLM·RAG 데이터 검수와 사람 피드백 수집에 특화 | 위와 같음 |

### 고를 때 주의할 점

- **검색 지표는 직접 구현하지 않는다.** `ranx`나 `ir-measures`를 쓰고, 노트의 손계산 예시를 테스트로 넣어 결과를 확인한다([05-regression-ci](./05-regression-ci/01-gate-design.md) L0).
- **이름이 같아도 정의가 다르다.** 예를 들어 `ragas`의 Context Recall은 정답 답변을 기준으로 계산하고, 노트의 Recall@k는 qrels를 기준으로 계산한다. 프레임워크 지표를 쓸 때는 계산 방식을 확인하고 노트의 지표와 이름을 구분해 기록한다.
- **프레임워크의 judge도 검증한다.** 내장 judge 프롬프트는 도구마다, 버전마다 다르다. 도구 이름과 버전을 기록하고 [04-llm-judge](./04-llm-judge/README.md) 방식대로 사람 판정과 맞춰 본다.
- **변화가 빠르다.** 이 목록은 2026년 11월 기준이다. 도입 전에 최신 문서, 유지 상태, 라이선스를 확인한다.

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.

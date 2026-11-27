# 골든셋 구축 (Golden Set)

골든셋은 평가에 쓰는 정답 데이터다. 질문, 질문별 정답 문서와 등급(qrels), 정답 답변으로 이루어진다. 지표가 아니라 지표가 비교할 **기준**이다. 이 README에는 기본으로 쓰는 골든셋의 구축 흐름, 사양, 판정 기준, 데이터 형식을 두고, 방법 설명은 하위 노트에 둔다.

- 골든셋으로 계산하는 지표는 [01-retrieval-metrics](../01-retrieval-metrics/README.md), [02-generation-metrics](../02-generation-metrics/README.md) 참고
- 정답 후보 1차 판정에 쓰는 judge는 [04-llm-judge](../04-llm-judge/README.md) 참고

## 하위 노트

- [00-generation-methods](./00-generation-methods.md): 단계별 일반적인 생성 방법 목록. 방법별 상세, 비교, 목적별 조합
- [01-query-sources](./01-query-sources.md): 평가 질문을 만드는 소스 A~D와 공통 정답 단계
- [02-pooling](./02-pooling.md): 여러 검색기 결과를 모아 정답 후보를 만드는 방법, 깊이, 한계
- [03-judging-and-review](./03-judging-and-review.md): LLM 1차 판정, 판정 병합과 최종 등급 규칙, 사람 검수 대상 고르기(무작위 표본, 우선 검수 신호, 멈추는 기준)
- [04-update-loop](./04-update-loop.md): 정답 기반·정답 없는 평가를 함께 돌리며 골든셋 누락과 노후화를 고치는 갱신 루프

## 골든셋의 위치

| 단계 | 하는 일 | 예 |
| --- | --- | --- |
| 골든셋 구축 (이 폴더) | 평가에 쓸 질문과 정답을 만든다 | 질문 소스 A~D, Pooling, 판정 |
| 지표 계산 | 골든셋을 기준으로 점수를 낸다 | Recall@k, Answer Correctness |
| 결과 분석 | 시스템끼리 비교하고 원인을 찾는다 | BM25 vs 하이브리드 |

Pooling, LLM judge는 지표가 아니라 정답을 만드는 과정이다.

## 구축 흐름

골든셋은 다섯 단계로 만든다. 이 흐름이 폴더의 지도이고, 단계마다 자세한 내용은 아래 표의 노트에 둔다.

```text
[1. 질문 만들기]
질문 소스: A 기존 질의응답(주력) / C 상황 시나리오(보완) / B 문서→질문(진단용) / D 사용 로그(로그가 쌓이면)
   │
질문 정제: 사용자·전문가 말투로 다시 쓰기, 유출 검사(문서 제목·문서 번호·원문 구절)
   │
   ▼
[2. 정답 후보 모으기]
Pool: 계열이 다른 검색기(BM25, 임베딩 2종, hybrid) 상위 20개 합집합 + seed + 질의 변형 검색 결과
   │
   ▼
[3. 판정과 검수]
Judge: LLM 1차 판정 (판정 기준은 아래 표)
   │
사람 검수: 무작위 표본 + 우선 검수 신호(seed 불일치, 경계 등급 1, 두 판정 불일치)
   │
   ▼
[4. 정답 답변 작성] (생성 평가용)
근거 문서로 확인 가능한 내용만, 핵심 주장 목록 함께
   │
   ▼
골든셋 vN 확정 (dev / test 분리)  ──▶  평가  ──▶  [5. 갱신]
```

| 단계 | 하는 일 | 일반적인 방법 ([00-generation-methods](./00-generation-methods.md)) | 자세한 노트 |
| --- | --- | --- | --- |
| 1. 질문 만들기 | 평가 질문을 얻고 정제한다 | Synthetic, Known-Item, User Log, 사람이 직접 작성 (2장) | [01-query-sources](./01-query-sources.md) |
| 2. 정답 후보 모으기 | 질문마다 정답일 수 있는 문서를 모은다 | Pooling, Weak Supervision (3장) | [02-pooling](./02-pooling.md) |
| 3. 판정과 검수 | 후보마다 등급을 매기고, 사람이 볼 항목을 골라 확정한다 | Human Annotation, LLM-as-a-Judge, Active Learning (4장, 5장) | [03-judging-and-review](./03-judging-and-review.md) |
| 4. 정답 답변 작성 | 생성 평가에 쓸 모범 답안과 핵심 주장 목록을 쓴다 | - | 아래 판정 기준의 "정답 답변 기준" |
| 5. 갱신 | 평가 결과로 누락·노후화를 찾아 골든셋을 고친다 | - | [04-update-loop](./04-update-loop.md) |

- 1~3단계는 어떤 방법을 쓰든 결과물이 같다. 질문, 후보 문서, 후보별 등급(qrels)이다. 방법을 바꿔도 이후 단계는 그대로 쓸 수 있다.
- 4단계는 생성 평가를 할 때만 필요하다. 검색 평가만 하면 3단계까지로 충분하다.

## 기본 사양

| 항목 | 결정 | 근거 |
| --- | --- | --- |
| 질문 소스 비중 | A 6 : C 3 : B 1. D는 로그가 쌓이면 C를 점차 대체 | [01-query-sources](./01-query-sources.md) 운영 원칙 |
| 질문 수 | 파일럿 50건 → 목표 200건 | 로드맵 50~200개 |
| 세는 단위 | 상황(건) 기준. 말투 변형(user / expert)은 판정을 공유하므로 문항 수는 최대 2배 | 01-query-sources 공통 정답 단계 |
| dev / test | 200건 기준 150 / 50. 소스별·답변 유형별 비율 유지 | [04-update-loop](./04-update-loop.md) 5장 |
| 답 없음 질의 | 전체의 약 10%. 절반 이상은 가까운 주제형 | [01-query-sources](./01-query-sources.md) "답 없음 질의 만들기" |
| 질문 구성 | 답변 유형·주제·난이도 목표 칸을 먼저 정하고 채움 | 아래 "질문 구성" |
| 판정 단위 | 문서(또는 섹션). 검색 결과는 청크 → 문서로 매핑 | [01-retrieval-metrics](../01-retrieval-metrics/01-reference-based.md) 3.2 |
| 등급 | 0 / 1 / 2 (아래 판정 기준) | - |
| 정답 인정 범위 | 이진 지표(Recall, Precision, MRR)에서는 **1 이상**을 정답으로 본다. nDCG는 등급 그대로 | 부분 근거(1)도 컨텍스트에 필요하므로 |
| Pool 참여 검색기 | 어휘 기반(BM25) + 서로 다른 계열 임베딩 2종 + hybrid + 질의 변형. 같은 모델의 dense·sparse·hybrid만으로는 부족 | [02-pooling](./02-pooling.md) 6장 |
| Pooling 깊이 | 상위 20 + seed | [02-pooling](./02-pooling.md) 4장 |
| Pool 점검 | 버전마다 유일 기여, leave-one-out, 사람 직접 검색(10건) | [02-pooling](./02-pooling.md) 6장 |
| 판정 | LLM 1차 판정 + 사람 검수. judge는 검증 통과 후 사용 | [04-llm-judge](../04-llm-judge/02-human-agreement.md) 7장, [03-judging-and-review](./03-judging-and-review.md) |
| 검수 | 무작위 표본 5~10% + 우선 검수 신호. 표본의 이진 뒤집힘 5% 이하면 나머지는 judge 판정 사용 | [03-judging-and-review](./03-judging-and-review.md) 3장 |
| 미판정 문서 | 평가 시 0으로 처리하고 Judged@k를 함께 기록 | 01-retrieval-metrics 3.4 |
| 판정 안 된 문항 | 평가에서 제외 | 01-query-sources 공통 정답 단계 |
| 점수 보고 | 소스별로 따로, 전체 평균은 참고 | 쉬운 소스(B)가 평균을 끌어올리는 것 방지 |

- 로드맵의 "실제 사용자 질문 로그로 골든셋 구축"은 D 단계의 목표다. 서비스를 열기 전까지는 A와 C로 실제 사용 분포에 가깝게 맞춘다.

### 질문 구성 (예시)

소스 비중만 정하면 질문이 한 유형에 쏠리기 쉽다. 목표 칸을 먼저 정하고, 칸마다 채우기 쉬운 소스로 채운다.

| 축 | 값 | 목표 (200건 기준) |
| --- | --- | --- |
| 답변 유형 (`answer_type`) | 단답 / 서술 / 다중 근거 / 답 없음 | 30% / 40% / 20% / 10% |
| 주제 (`topic`) | 색인 범위의 문서 영역 | 영역마다 최소 5건 |
| 난이도 (`difficulty`) | 쉬움 / 보통 / 어려움 | 3 : 4 : 3 |

| 난이도 | 기준 |
| --- | --- |
| 쉬움 | 근거 문서 1개, 질문과 문서 표현이 비슷함 |
| 보통 | 근거 문서 1개, 표현이 다르거나 조건이 하나 붙음 |
| 어려움 | 근거 문서 2개 이상, 또는 예외 조건을 알아야 답할 수 있음 |

- 답변 유형 × 주제 칸마다 최소 건수를 두고 빈 칸을 추적한다. 예를 들어 A 소스로 채우기 어려운 일상 주제 칸은 C로 채운다.
- 난이도는 판정이 끝난 뒤 정답 문서 수와 표현 차이를 보고 확정한다. 질문을 쓸 때 매긴 값은 임시값이다.
- 점수는 소스별과 함께 유형별·난이도별로도 본다. 평균이 같아도 어려운 질문에서만 떨어지는 변경을 잡을 수 있다.

### Pooling 깊이와 평가 k

- Pool이 상위 20이면 각 검색기의 20위 안쪽은 판정되어 있고, 21위 아래는 대부분 미판정이다.
- 그래서 **k ≤ 20인 지표는 그대로 믿을 수 있고**, Recall@50 같은 깊은 지표는 21~50위 정답을 놓쳐 낮게 나온다.
- Recall@50(리랭커 1차 후보)은 **참고용**으로 쓰고 Judged@50을 함께 기록한다. 정확히 재야 하면 Pooling 깊이를 50으로 올린다(판정 비용 약 2.5배).

## 판정 기준 (등급 원본)

사람 판정자, LLM judge, 갱신 루프가 모두 **이 문장 그대로** 쓴다. 기준을 바꾸면 골든셋 메이저 버전을 올린다([04-update-loop](./04-update-loop.md) 7장).

| 등급 | 이름 | 정의 | 판정 질문 |
| --- | --- | --- | --- |
| 2 | 관련 | 이 자료만으로 질문에 답할 수 있다 (핵심 근거) | 이 자료를 읽으면 답을 쓸 수 있는가? |
| 1 | 부분 관련 | 답의 일부나 필요한 조건을 담고 있지만 이것만으로는 답할 수 없다 (부수 근거) | 답을 쓰는 데 도움은 되지만 다른 자료가 더 필요한가? |
| 0 | 무관 | 같은 주제어가 나와도 질문에 답하는 데 쓸 수 없다 | 이 자료가 없어도 답에 영향이 없는가? |

경계 규칙
- 주제어만 겹치고 답에 필요한 정보가 없으면 **0**이다. 단어 겹침으로 1을 주지 않는다.
- 개정 전 문서처럼 오래된 자료도 관련성은 내용으로 판정한다. 최신성은 `doc_version`으로 따로 점검한다.
- 판정 예시와 judge 프롬프트는 [04-llm-judge/01-rubric-design](../04-llm-judge/01-rubric-design.md) 2장 참고

정답 답변 기준 (생성 평가용)
- 근거 문서에서 확인할 수 있는 내용만 쓴다. 근거에 없는 내용이 정답에 있으면 충실한 답변이 감점된다.
- 핵심 주장 목록(`reference_claims`)을 함께 적는다. Claim Recall과 정답 비교 judge가 이 목록을 쓴다.
- 답 없음 질의의 정답 답변은 `답 없음`으로 둔다.
- 작성은 LLM 초안 → 사람이 근거 문서와 대조해 고치고 확정하는 순서로 한다. 핵심 주장 목록을 쪼갠 결과도 사람이 확인한다.

## 데이터 형식

질문 파일과 판정 파일 두 개로 관리한다.

### 질문 (`questions.jsonl`)

```json
{
  "query_id": "Q001-user",
  "case_id": "Q001",
  "question": "결제를 취소했는데 일주일째 환불이 안 들어오면 어떻게 하나요?",
  "variant": "user",
  "source": "C",
  "answer_type": "서술",
  "topic": "환불",
  "difficulty": "보통",
  "evidence_sets": [["DOC_0003", "DOC_0004"]],
  "reference_answer": "...",
  "reference_claims": ["...", "..."],
  "split": "dev",
  "golden_set_version": "v1.0",
  "created_at": "YYYY-MM-DD"
}
```

| 필드 | 내용 | 쓰는 곳 |
| --- | --- | --- |
| `query_id` | 문항 ID | 모든 지표 |
| `case_id` | 상황 ID. 말투 변형끼리 같은 값, 판정 공유 | qrels 연결 |
| `variant` | `user` / `expert` | 말투별 점수 비교 |
| `source` | `A` / `B` / `C` / `D` | 소스별 점수 보고 |
| `answer_type` | `단답` / `서술` / `다중 근거` / `답 없음` | 생성 지표 유형별 선택, 거절 정확도 |
| `topic` | 문서 영역 | 질문 구성 칸 추적, 주제별 점수 |
| `difficulty` | `쉬움` / `보통` / `어려움` | 난이도별 점수 |
| `evidence_sets` | 함께 있어야 답이 되는 문서 조합 목록. 조합 중 하나를 다 갖추면 답할 수 있음 (다중 근거 질문만) | 조합 단위 Recall: 조합 전체가 top-k에 들었나 |
| `reference_answer` | 정답 답변 | Answer Correctness |
| `reference_claims` | 정답 핵심 주장 목록 | Claim Recall |
| `split` | `dev` / `test` | 튜닝용·확인용 분리 |
| `golden_set_version` | 골든셋 버전 | 결과 비교 가능 여부 |

### 판정 (`qrels.csv`)

```csv
case_id,doc_id,doc_version,relevance,evidence_span,judged_by
Q001,DOC_0003,2024-01-01,2,"...",human
Q001,DOC_0004,2024-01-01,1,,llm+human
Q001,DOC_0120,2023-06-01,0,,llm+human
```

| 필드 | 내용 | 쓰는 곳 |
| --- | --- | --- |
| `case_id` | 상황 ID | 질문 연결 |
| `doc_id` | 문서 고정 ID | 검색 지표 |
| `doc_version` | 문서 개정일 | 노후화 점검 ([04-update-loop](./04-update-loop.md) 6장) |
| `relevance` | 0 / 1 / 2 | 검색 지표 |
| `evidence_span` | 정답 근거 문장 (선택) | 청킹 비교용 판정 (01-retrieval-metrics 3.2 C 방식) |
| `judged_by` | `llm` / `human` / `llm+human` | judge 검증, 갱신 이력 |

- 판정한 문서만 적는다. 이 파일에 없는 문서는 미판정이다.
- 변경 이력은 별도 파일로 관리한다([04-update-loop](./04-update-loop.md) 7장).

## 관련 코드

- 골든셋 구축 코드와 데이터는 lawlens 프로젝트에 있다 ([99-projects/01-lawlens](../../99-projects/01-lawlens.md))
  - A 소스: [`build_expc.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/build_expc.py), [`rewrite_expc.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/rewrite_expc.py)
  - B 소스: [`build_synth.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/build_synth.py)
  - C 소스: [`scenario.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/scenario.py)
  - 공통 정답 단계: [`pool.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/pool.py), [`judge.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/judge.py)
  - 데이터: [`datasets/`](https://github.com/Aegith-Ha/LawLens/tree/main/eval/datasets) (`expc_rewrite.*`, `scenario.*`, `synth.*`)
- 실행 방법은 lawlens 프로젝트 README 참고

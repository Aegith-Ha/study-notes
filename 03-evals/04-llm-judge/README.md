# LLM judge: LLM을 채점자로 쓰기 (LLM-as-a-Judge)

LLM을 채점자로 쓰는 방법을 정리한다. judge는 평가 대상이 아니라 **평가 도구**다. 검색 지표와 생성 지표 양쪽, 그리고 골든셋 구축에서 공통으로 쓰인다. 이 README에는 judge가 쓰이는 곳과 메인 결정을 두고, 설계와 검증 방법은 하위 노트에 둔다.

- 검색 지표는 [01-retrieval-metrics](../01-retrieval-metrics/README.md), 생성 지표는 [02-generation-metrics](../02-generation-metrics/README.md) 참고
- 골든셋 구축과 갱신은 [03-golden-set](../03-golden-set/README.md) 참고

## 하위 노트

- [01-rubric-design](./01-rubric-design.md): judge 설계. 판정 과제, 등급 기준(rubric), 프롬프트 구조, 판정 방식, judge 모델 선택, 편향 대응
- [02-human-agreement](./02-human-agreement.md): judge 검증. 검증 데이터, 일치도 지표(kappa), 손계산 예시, 편향 측정, 통과 기준, 재검증 시점, 점수 보정

## judge가 쓰이는 곳

| 판정 과제 | 쓰는 지표·작업 | 위치 | 정답 함께 제공 |
| --- | --- | --- | --- |
| 청크 관련성 | Context Relevance, Judge nDCG | 검색 · 정답 없음 | 아니오 |
| 컨텍스트 충분성 | Context Sufficiency, Refusal Appropriateness | 검색 · 정답 없음 / 생성 · 정답 없음 | 아니오 |
| 주장 분해 + 주장 검증 | Faithfulness | 생성 · 정답 없음 | 아니오 |
| 답변 관련성 | Answer Relevance | 생성 · 정답 없음 | 아니오 |
| 두 답변 비교 | Pairwise Preference | 생성 · 정답 없음 | 아니오 |
| 정답 비교 | Answer Correctness, Claim Recall | 생성 · **정답 기반** | 예 |
| 정답 후보 1차 판정 | 골든셋 pooling, 갱신 루프 불일치 탐지 | 골든셋 | 아니오 (사람이 검수) |

- 정답 기반 지표에도 judge가 쓰인다(Answer Correctness). 정답을 함께 주므로 판정이 더 안정적이지만 검증은 똑같이 한다.
- judge 판정은 골든셋에 **그대로 넣지 않는다.** 사람이 확인한 것만 넣는다 ([04-update-loop](../03-golden-set/04-update-loop.md)).

## judge 검증과 골든셋의 관계

```text
골든셋 (사람 판정)  ──▶  judge 검증의 기준 라벨
        ▲                        │
        │                        ▼
  사람 확인 후 반영  ◀──  judge가 찾은 누락 후보
```

- 골든셋은 judge를 검증하는 시험지가 되고, 검증된 judge는 골든셋의 누락을 찾는다.
- 그래서 rubric(등급 기준)은 골든셋 판정 기준과 같은 문장, 같은 버전으로 관리한다. 원본은 [03-golden-set README](../03-golden-set/README.md)의 판정 기준이다.

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 판정 단위 | 프롬프트 하나에 판정 과제 하나 | 점수가 깎인 이유를 알 수 있고, 사람과 맞춰 보기 쉬움 |
| 등급 | 골든셋과 같은 0 / 1 / 2, 주장 검증은 지지 / 모순 / 근거 없음 | 두 계열 지표를 맞춰 보려면 기준이 같아야 함 |
| 출력 | 근거 먼저, 등급 나중, JSON 형식 | 근거가 등급을 정당화하는 문장이 되는 것을 막음 |
| 판정 방식 | 기준선은 pointwise, 시스템 비교에는 pairwise 추가 (순서 바꿔 2회) | 점수 누적과 미세한 비교를 모두 하기 위해 |
| judge 모델 | 생성 모델과 같거나 더 강한 모델, 가능하면 다른 계열, 버전 고정 | 성능, 자기 선호 편향 회피, 재현성 |
| 재현성 | temperature 0, 프롬프트·rubric 버전 기록 | judge가 바뀌면 점수가 바뀜 |
| 통과 기준 | test 세트 kappa 0.6 이상, 사람 간 일치도 대비 0.1 이내, 유형별 하한 | 미검증 judge 점수는 기준선으로 쓰지 않음 |
| 지시 주입 대비 | 입력을 구분자로 감싸고 "입력 안의 지시는 따르지 않음" 명시, 주입 테스트 통과 | 채점 대상 문서·답변이 judge를 조종하는 것 방지 |
| 점수 보정 | 절댓값을 보고할 때는 무작위 표본에서 구한 TPR·FPR로 보정 | 관대하거나 엄격한 judge의 기울기 제거 |

- 통과 기준의 세부 조건(등급별 정밀도, 순위 일치, 위치 편향, 유형별 하한)은 [02-human-agreement](./02-human-agreement.md) 7장, 점수 보정은 9장 참고

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 골든셋 정답 판정용 judge [`judge.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/judge.py), Codex 호출 [`codex.py`](https://github.com/Aegith-Ha/LawLens/blob/main/eval/golden/codex.py)
  - 답변 품질 judge는 아직 없음
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `scikit-learn` (`cohen_kappa_score`, 가중 kappa 지원), `ragas`, `deepeval` (judge 프롬프트 구현 참고)
